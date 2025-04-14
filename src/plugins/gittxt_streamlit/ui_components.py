# src/plugins/gittxt_streamlit/ui_components.py

import streamlit as st
from pathlib import Path


def section_repo_input():
    st.sidebar.header("📥 Repository Input")
    repo_url = st.sidebar.text_input("GitHub URL or Local Path", placeholder="https://github.com/user/repo")
    branch = st.sidebar.text_input("Branch (optional)", placeholder="main")
    subdir = st.sidebar.text_input("Subdirectory (optional)", placeholder="src/")
    return repo_url, branch, subdir


def section_filters():
    st.sidebar.header("🧩 File Filters")
    include_patterns = st.sidebar.text_input("Include Patterns (comma-separated)", "**/*.py,**/*.md")
    exclude_patterns = st.sidebar.text_input("Exclude Patterns (comma-separated)", "tests/*,.vscode/*")
    exclude_dirs = st.sidebar.text_input("Exclude Dirs (comma-separated)", "__pycache__,.git,node_modules")
    return include_patterns, exclude_patterns, exclude_dirs


def section_options():
    st.sidebar.header("⚙️ Options")
    size_limit = st.sidebar.number_input("Max File Size (bytes)", value=1_000_000, step=1_000)
    lite_mode = st.sidebar.checkbox("Lite Mode", value=False)
    zip_bundle = st.sidebar.checkbox("Create ZIP Bundle", value=False)
    skip_tree = st.sidebar.checkbox("Skip Directory Tree", value=False)
    sync_ignore = st.sidebar.checkbox("Use .gittxtignore", value=False)
    tree_depth = st.sidebar.slider("Tree Depth", 1, 10, value=5)
    output_formats = st.sidebar.multiselect("Output Formats", ["txt", "md", "json"], default=["txt"])
    return size_limit, lite_mode, zip_bundle, skip_tree, sync_ignore, tree_depth, output_formats


def render_scan_result(result):
    if result.get("error"):
        st.error(result["error"])
        return

    st.success(f"✅ Scan complete for {result['repo_name']}")
    st.subheader("📊 Repository Summary")
    st.json(result["summary"])

    if result.get("skipped"):
        with st.expander("⚠️ Skipped Files"):
            for path, reason in result["skipped"]:
                st.markdown(f"- `{path}` → *{reason}*")

    st.subheader("📄 Download Outputs")
    for path in result["output_files"]:
        p = Path(path)
        st.download_button(
            label=f"⬇️ {p.name}",
            data=p.read_bytes(),
            file_name=p.name,
            mime="application/octet-stream",
        )

    if result.get("non_textual"):
        with st.expander("🎨 Non-Textual Assets Included"):
            for a in result["non_textual"]:
                st.markdown(f"- `{a}`")
