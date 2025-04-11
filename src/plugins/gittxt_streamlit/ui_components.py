import streamlit as st
from pathlib import Path
from gittxt.utils.subcat_utils import detect_subcategory
from collections import defaultdict


def display_summary(repo_info: dict):
    summary = repo_info.get("summary", {})
    st.subheader("📊 Repository Summary")
    st.markdown(f"**Repo Name**: `{repo_info['repo_name']}`")
    st.markdown(f"**Total Files**: `{summary.get('total_files', 0)}`")
    st.markdown(f"**Estimated Tokens**: `{summary.get('formatted', {}).get('estimated_tokens', '-')}`")
    st.markdown(f"**Total Size**: `{summary.get('formatted', {}).get('total_size', '-')}`")


def display_directory_tree(repo_info: dict):
    st.subheader("🌲 Directory Tree")
    st.code(repo_info.get("tree_summary", "(No tree available)"), language="text")


def display_file_type_selector(repo_info: dict):
    st.subheader("📂 File Type Classification")

    # Extract extensions from textual and non-textual files
    ext_counts = defaultdict(int)
    for path in repo_info.get("textual_files", []) + repo_info.get("non_textual_files", []):
        ext = path.suffix.lower()
        if ext:
            ext_counts[ext] += 1

    textual_exts = {p.suffix.lower() for p in repo_info.get("textual_files", []) if p.suffix}
    non_textual_exts = {p.suffix.lower() for p in repo_info.get("non_textual_files", []) if p.suffix}

    # Render two columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Textual Extensions (editable)**")
        editable_textual = st.multiselect(
            "Mark as Textual:",
            options=sorted(ext_counts),
            default=sorted(textual_exts),
            key="textual_selector"
        )
    with col2:
        st.markdown("**Non-Textual Extensions (locked)**")
        locked = sorted(non_textual_exts - set(editable_textual))
        st.write(", ".join(locked) or "-")

    return editable_textual


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
    st.subheader("📥 Download Outputs")
    for fmt, path in outputs.items():
        if Path(path).exists():
            with open(path, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download {fmt.upper()} Output",
                    data=f.read(),
                    file_name=Path(path).name,
                    mime="application/octet-stream",
                    key=f"download_{fmt}"
                )
