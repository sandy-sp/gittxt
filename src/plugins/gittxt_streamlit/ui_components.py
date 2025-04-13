import streamlit as st
from pathlib import Path
from gittxt.utils.subcat_utils import detect_subcategory
from collections import defaultdict
import asyncio
import pandas as pd
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT


def get_data_path(row):
    return row["full_path"].split("/")


async def _classify_extensions_by_subcategory(textual_file_paths):
    subcat_exts = defaultdict(set)
    for file_path in textual_file_paths:
        file = Path(file_path)
        subcat = await detect_subcategory(file, "TEXTUAL")
        ext = file.suffix.lower()
        if ext:
            subcat_exts[subcat].add(ext)
    return subcat_exts


def display_summary(repo_info: dict):
    summary = repo_info.get("summary", {})
    formatted = summary.get("formatted", {})

    st.subheader("**Repository Summary**")
    st.markdown(f"**Repo Name**: `{repo_info['repo_name']}`")
    st.markdown(f"**Total Files**: `{summary.get('total_files', 0)}`")
    st.markdown(f"**Total Size**: `{formatted.get('total_size', '-')}`")
    st.markdown(f"**Estimated Tokens**: `{formatted.get('estimated_tokens', '-')}`")

    branch = repo_info.get("branch") or "main"
    repo_url = repo_info.get("repo_url", "(local)")
    st.markdown(f"**Branch**: `{branch}`")
    st.markdown(f"**Source URL**: [{repo_url}]({repo_url})")

    st.markdown("### File Type Breakdown and Tokens")
    file_type_breakdown = summary.get("file_type_breakdown", {})
    tokens_by_type = formatted.get("tokens_by_type", {})

    if file_type_breakdown:
        df = pd.DataFrame({
            "File Type": list(file_type_breakdown.keys()),
            "Files": list(file_type_breakdown.values()),
            "Tokens": [tokens_by_type.get(ft, "-") for ft in file_type_breakdown.keys()],
        })
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No file type breakdown available.")


def display_directory_tree(repo_info: dict):
    st.subheader("Directory Tree")
    tree = repo_info.get("tree_summary", "").strip() or "(No tree available)"

    with st.expander("Show/Hide Directory Tree", expanded=False):
        st.code(tree, language="plaintext")


def display_file_type_selector(repo_info: dict):
    textual_files = repo_info.get("textual_file_paths", [])
    subcat_exts = asyncio.run(_classify_extensions_by_subcategory(textual_files))
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
    filters = {
        "repo_path": repo_info["repo_path"],
        "repo_name": repo_info["repo_name"],
        "textual_file_paths": repo_info["textual_file_paths"],
        "non_textual_file_paths": repo_info["non_textual_file_paths"],
        "branch": repo_info.get("branch"),
        "subdir": repo_info.get("subdir"),
        "repo_url": repo_info.get("repo_url"),
    }

    st.subheader("Output Formats")
    formats = ["txt", "json", "md"]
    selected_formats = [fmt for fmt in formats if st.checkbox(f"Include {fmt.upper()} Format", value=(fmt == "txt"), key=f"format_{fmt}")]
    filters["output_formats"] = selected_formats

    filters["lite_mode"] = st.checkbox("Lite Mode", value=False, key="lite")
    filters["zip_output"] = st.checkbox("Include ZIP Bundle", value=True, key="zip")

    with st.expander("⚙️ Advanced Filters: File Types + Rules"):
        filters["custom_textual"] = display_file_type_selector(repo_info)

        tree_lines = repo_info.get("tree_summary", "").split("\n")
        all_dirs = sorted({line.strip(" │├└─") for line in tree_lines if line.strip() and "." not in line})
        filters["exclude_dirs"] = st.multiselect("Exclude Directories:", all_dirs, key="exclude_dirs")
        filters["include_patterns"] = [p.strip() for p in st.text_input("Include Patterns (comma-separated):", key="include_patterns").split(",") if p.strip()]
        filters["exclude_patterns"] = [p.strip() for p in st.text_input("Exclude Patterns (comma-separated):", key="exclude_patterns").split(",") if p.strip()]

    return filters


def display_outputs(outputs: dict):
    st.subheader("Download Outputs")
    if outputs:
        for fmt, path in outputs.items():
            file_path = Path(path)
            if file_path.exists():
                with open(file_path, "rb") as f:
                    st.download_button(
                        label=f"\u2b07\ufe0f Download {fmt.upper()}",
                        data=f.read(),
                        file_name=file_path.name,
                        mime="application/octet-stream",
                        key=f"download_{fmt}"
                    )


def display_hidden_icon_with_tooltip():
    st.markdown(f"""
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
            bottom: 125%;
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
    """, unsafe_allow_html=True)
