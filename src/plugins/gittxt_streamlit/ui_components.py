# src/plugins/gittxt_streamlit/ui_components.py

import streamlit as st
from pathlib import Path


def section_filters():
    with st.expander("⚙️ Advanced Filters"):
        include_patterns = st.text_input("Include Patterns (comma-separated)", "**/*.py,**/*.md")
        exclude_patterns = st.text_input("Exclude Patterns (comma-separated)", "tests/*,.vscode/*")
        exclude_dirs = st.text_input("Exclude Dirs (comma-separated)", "__pycache__,.git,node_modules")
        max_file_size = st.slider("Max File Size (bytes)", min_value=0, max_value=5_000_000, step=100_000, value=1_000_000)
        tree_depth = st.slider("Tree Depth", 1, 10, value=5)
    return include_patterns, exclude_patterns, exclude_dirs, max_file_size, tree_depth


def section_options():
    lite_mode = st.checkbox("Lite Mode", value=False)
    zip_bundle = st.checkbox("Create ZIP Bundle", value=False)
    skip_tree = st.checkbox("Skip Directory Tree", value=False)
    sync_ignore = st.checkbox("Use .gittxtignore", value=False)

    st.markdown("**Output Formats:**")
    txt = st.checkbox(".txt", value=True)
    md = st.checkbox(".md", value=True)
    json = st.checkbox(".json", value=True)
    selected_formats = [fmt for fmt, checked in zip(["txt", "md", "json"], [txt, md, json]) if checked]

    return lite_mode, zip_bundle, skip_tree, sync_ignore, selected_formats


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
