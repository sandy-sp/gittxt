import streamlit as st
from pathlib import Path
from gittxt.utils.subcat_utils import detect_subcategory
from collections import defaultdict
import asyncio
import pandas as pd
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT  # Import the default excluded directories


def get_data_path(row):
    """Helper function to extract the data path for treeData."""
    return row["full_path"].split("/")


async def _classify_extensions_by_subcategory(textual_files):
    subcat_exts = defaultdict(set)
    for file in textual_files:
        subcat = await detect_subcategory(file, "TEXTUAL")
        ext = file.suffix.lower()
        if ext:
            subcat_exts[subcat].add(ext)
    return subcat_exts


def display_summary(repo_info: dict):
    """
    Display the repository summary in the Streamlit UI.
    """
    summary = repo_info.get("summary", {})
    formatted = summary.get("formatted", {})

    st.subheader("**Repository Summary**")
    st.markdown(f"**Repo Name**: `{repo_info['repo_name']}`")
    st.markdown(f"**Total Files**: `{summary.get('total_files', 0)}`")
    st.markdown(f"**Total Size**: `{formatted.get('total_size', '-')}`")
    st.markdown(f"**Estimated Tokens**: `{formatted.get('estimated_tokens', '-')}`")

    # Display file type breakdown
    st.markdown("### File Type Breakdown")
    file_type_breakdown = summary.get("file_type_breakdown", {})
    if file_type_breakdown:
        for file_type, count in file_type_breakdown.items():
            st.markdown(f"- **{file_type.capitalize()}**: `{count}` files")
    else:
        st.markdown("No file type breakdown available.")

    # Display tokens by type
    st.markdown("### Tokens by File Type")
    tokens_by_type = formatted.get("tokens_by_type", {})
    if tokens_by_type:
        for file_type, tokens in tokens_by_type.items():
            st.markdown(f"- **{file_type.capitalize()}**: `{tokens}` tokens")
    else:
        st.markdown("No token data available.")


def display_directory_tree(repo_info: dict):
    st.subheader("Directory Tree")
    tree = repo_info.get("tree_summary", "(No tree available)")

    # Add a collapsible section using st.expander
    with st.expander("Show/Hide Directory Tree", expanded=False):
        # Wrap the tree in a styled container
        st.markdown(
            """
            <style>
            .tree-container {
                max-height: 200px;
                overflow-y: auto;
                background-color: #111;
                padding: 1em;
                border-radius: 5px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Use st.code for proper formatting inside the styled container
        st.markdown('<div class="tree-container">', unsafe_allow_html=True)
        st.code(tree, language="plaintext")
        st.markdown('</div>', unsafe_allow_html=True)


def display_file_type_selector(repo_info: dict):
    st.subheader("File Type Classification by Subcategory")
    subcat_exts = asyncio.run(_classify_extensions_by_subcategory(repo_info["textual_files"]))

    selected_exts = set()
    cols = st.columns(2)
    for idx, (subcat, extensions) in enumerate(sorted(subcat_exts.items())):
        with cols[idx % 2]:
            st.markdown(f"**{subcat.upper()}**")
            chosen = st.multiselect(
                f"Include extensions for {subcat}",
                options=sorted(extensions),
                default=sorted(extensions),
                key=f"subcat_{subcat}"
            )
            selected_exts.update(chosen)

    return sorted(selected_exts)


def display_filter_form(repo_info: dict):
    filters = {}
    filters["repo_path"] = repo_info["repo_path"]
    filters["repo_name"] = repo_info["repo_name"]
    filters["textual_files"] = repo_info["textual_files"]
    filters["non_textual_files"] = repo_info["non_textual_files"]
    filters["handler"] = repo_info["handler"]

    # Add checkboxes for default excludes and .gitignore
    st.subheader("Repository Options")
    filters["include_default_excludes"] = st.checkbox(
        "Include Default Excluded Directories", value=True, key="default_excludes"
    )
    filters["include_gitignore"] = st.checkbox(
        "Include .gitignore Rules", value=True, key="gitignore_rules"
    )

    # Extract dirs from tree
    tree_lines = repo_info.get("tree_summary", "").split("\n")
    all_dirs = sorted({line.strip("│├└─ ") for line in tree_lines if line.strip() and not "." in line})
    filters["exclude_dirs"] = st.multiselect("Exclude Directories:", all_dirs, key="exclude_dirs")

    filters["include_patterns"] = st.text_input("Include Patterns (comma-separated):", key="include_patterns").split(",")
    filters["exclude_patterns"] = st.text_input("Exclude Patterns (comma-separated):", key="exclude_patterns").split(",")

    # Custom textual extension overrides
    filters["custom_textual"] = display_file_type_selector(repo_info)

    filters["size_limit"] = st.slider("Max File Size (KB):", min_value=1, max_value=1000, value=200) * 1024
    filters["output_formats"] = st.multiselect("Output Formats:", ["txt", "json", "md"], default=["txt"], key="formats")
    filters["lite_mode"] = st.checkbox("Lite Mode", value=False, key="lite")
    filters["zip_output"] = st.checkbox("Include ZIP Bundle", value=True, key="zip")
    filters["tree_depth"] = st.slider("Tree Depth (optional):", min_value=1, max_value=10, value=4)

    return filters


def display_outputs(outputs: dict):
    st.subheader("Download Outputs")
    for fmt, path in outputs.items():
        if Path(path).exists():
            with open(path, "rb") as f:
                st.download_button(
                    label=f"\u2b07\ufe0f Download {fmt.upper()} Output",
                    data=f.read(),
                    file_name=Path(path).name,
                    mime="application/octet-stream",
                    key=f"download_{fmt}"
                )


def display_hidden_icon_with_tooltip():
    # Create a hidden icon with a tooltip
    st.markdown(
        f"""
        <style>
        .tooltip {{
            position: relative;
            display: inline-block;
            cursor: pointer;
        }}

        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 5px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%; /* Position above the icon */
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }}

        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
        </style>
        <div class="tooltip">
            ❓
            <span class="tooltiptext">
                Default Excluded Directories:<br>
                {", ".join(EXCLUDED_DIRS_DEFAULT)}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
