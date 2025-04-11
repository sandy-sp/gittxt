import streamlit as st
from pathlib import Path
from gittxt.utils.subcat_utils import detect_subcategory
from collections import defaultdict
import asyncio


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
    st.subheader("**Repository Summary**")
    st.markdown(f"**Repo Name**: `{repo_info['repo_name']}`")
    st.markdown(f"**Total Files**: `{summary.get('total_files', 0)}`")
    st.markdown(f"**Estimated Tokens**: `{summary.get('formatted', {}).get('estimated_tokens', '-')}`")
    st.markdown(f"**Total Size**: `{summary.get('formatted', {}).get('total_size', '-')}`")


def display_directory_tree(repo_info: dict):
    st.subheader("Directory Tree")
    st.code(repo_info.get("tree_summary", "(No tree available)"), language="text")


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
