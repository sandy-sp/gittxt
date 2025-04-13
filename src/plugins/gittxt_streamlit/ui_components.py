import streamlit as st
from pathlib import Path
from gittxt.utils.subcat_utils import detect_subcategory
from collections import defaultdict
import asyncio
import pandas as pd
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT


def get_data_path(row):
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
    summary = repo_info.get("summary", {})
    formatted = summary.get("formatted", {})
    handler = repo_info.get("handler")

    st.subheader("**Repository Summary**")
    st.markdown(f"**Repo Name**: `{repo_info['repo_name']}`")
    st.markdown(f"**Total Files**: `{summary.get('total_files', 0)}`")
    st.markdown(f"**Total Size**: `{formatted.get('total_size', '-')}`")
    st.markdown(f"**Estimated Tokens**: `{formatted.get('estimated_tokens', '-')}`")

    if handler:
        branch = handler.branch or "main"
        url = getattr(handler, "repo_url", None) or "(local)"
        st.markdown(f"**Branch**: `{branch}`")
        st.markdown(f"**Source URL**: [{url}]({url})")

    st.markdown("### File Type Breakdown and Tokens")
    file_type_breakdown = summary.get("file_type_breakdown", {})
    tokens_by_type = formatted.get("tokens_by_type", {})

    if file_type_breakdown:
        df = pd.DataFrame({
            "File Type": list(file_type_breakdown.keys()),
            "Files": list(file_type_breakdown.values()),
            "Tokens": [tokens_by_type.get(ft, "-") for ft in file_type_breakdown.keys()],
        })
        styled = df.style.set_table_styles(
            [
                {"selector": "td", "props": [("text-align", "center")]},
                {"selector": "th", "props": [("text-align", "center")]}]
        ).hide(axis="index").to_html()

        style_block, table_html = styled.split('<style type="text/css">', 1)
        style_block = f"<style>{table_html.split('</style>', 1)[0]}</style>"
        table_html = table_html.split('</style>', 1)[1]

        st.markdown(style_block, unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center;'>{table_html}</div>", unsafe_allow_html=True)
    else:
        st.info("No file type breakdown available.")


def display_directory_tree(repo_info: dict):
    st.subheader("Directory Tree")
    tree = repo_info.get("tree_summary", "").strip() or "(No tree available)"

    with st.expander("Show/Hide Directory Tree", expanded=False):
        st.markdown("""
            <style>
            .tree-container {
                max-height: 200px;
                overflow-y: auto;
                background-color: #111;
                padding: 1em;
                border-radius: 5px;
            }
            </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="tree-container">', unsafe_allow_html=True)
        st.code(tree, language="plaintext")
        st.markdown('</div>', unsafe_allow_html=True)


def display_file_type_selector(repo_info: dict):
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
    filters = {
        "repo_path": repo_info["repo_path"],
        "repo_name": repo_info["repo_name"],
        "textual_files": repo_info["textual_files"],
        "non_textual_files": repo_info["non_textual_files"],
        "handler": repo_info["handler"],
    }

    st.subheader("Output Formats")
    formats = ["txt", "json", "md"]
    selected_formats = [fmt for fmt in formats if st.checkbox(f"Include {fmt.upper()} Format", value=(fmt == "txt"), key=f"format_{fmt}")]
    filters["output_formats"] = selected_formats

    filters["lite_mode"] = st.checkbox("Lite Mode", value=False, key="lite")
    filters["zip_output"] = st.checkbox("Include ZIP Bundle", value=True, key="zip")

    st.subheader("Repository Options")
    filters["include_default_excludes"] = st.checkbox("Include Default Excluded Directories", value=True, key="default_excludes")
    filters["include_gitignore"] = st.checkbox("Include .gitignore Rules", value=True, key="gitignore_rules")

    with st.expander("⚙️ Advanced Filters: File Types + Rules"):
        filters["custom_textual"] = display_file_type_selector(repo_info)

        tree_lines = repo_info.get("tree_summary", "").split("\n")
        all_dirs = sorted({line.strip("│├└─ ") for line in tree_lines if line.strip() and "." not in line})
        filters["exclude_dirs"] = st.multiselect("Exclude Directories:", all_dirs, key="exclude_dirs")
        filters["include_patterns"] = st.text_input("Include Patterns (comma-separated):", key="include_patterns").split(",")
        filters["exclude_patterns"] = st.text_input("Exclude Patterns (comma-separated):", key="exclude_patterns").split(",")

    return filters


def display_outputs(outputs: dict):
    st.subheader("Download Outputs")
    if outputs:
        st.markdown("""
        <style>
        .block-container .element-container .stDownloadButton {
            display: inline-block;
            margin-right: 4px;
        }
        </style>
        """, unsafe_allow_html=True)
        for fmt, path in outputs.items():
            if Path(path).exists():
                with open(path, "rb") as f:
                    st.download_button(
                        label=f"\u2b07\ufe0f {fmt.upper()}",
                        data=f.read(),
                        file_name=Path(path).name,
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
