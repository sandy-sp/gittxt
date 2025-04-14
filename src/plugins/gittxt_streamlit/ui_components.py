# src/plugins/gittxt_streamlit/ui_components.py

import streamlit as st
from pathlib import Path


def section_filters():
    include_patterns = st.text_input("Include Patterns (comma-separated)", "**/*.py,**/*.md")
    exclude_patterns = st.text_input("Exclude Patterns (comma-separated)", "tests/*,.vscode/*")
    exclude_dirs = st.text_input("Exclude Dirs (comma-separated)", "__pycache__,.git,node_modules")
    return include_patterns, exclude_patterns, exclude_dirs


def section_options():
    size_limit = st.number_input("Max File Size (bytes)", value=1_000_000, step=1_000)
    lite_mode = st.checkbox("Lite Mode", value=False)
    zip_bundle = st.checkbox("Create ZIP Bundle", value=False)
    skip_tree = st.checkbox("Skip Directory Tree", value=False)
    sync_ignore = st.checkbox("Use .gittxtignore", value=False)
    tree_depth = st.slider("Tree Depth", 1, 10, value=5)
    output_formats = st.multiselect("Output Formats", ["txt", "md", "json"], default=["txt"])
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
