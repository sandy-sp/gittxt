import pandas as pd
import streamlit as st
from pathlib import Path
import humanize


def section_filters():
    with st.expander("⚙️ Advanced Filters"):
        include_patterns = st.text_input("Include Patterns (comma-separated)", placeholder= "**/*.py,**/*.md")
        exclude_patterns = st.text_input("Exclude Patterns (comma-separated)", placeholder= "tests/*,.vscode/*")
        exclude_dirs = st.text_input("Exclude Dirs (comma-separated)", placeholder= "__pycache__,.git,node_modules")
        max_file_size_mb = st.slider("Max File Size (MB)", min_value=0, max_value=73, step=1, value=1)
        max_file_size = max_file_size_mb * 1_000_000
        tree_depth = st.slider("Tree Depth", 1, 10, value=5)
    return include_patterns, exclude_patterns, exclude_dirs, max_file_size, tree_depth


def section_options():
    st.subheader("📦 Download Options")
    col1, col2 = st.columns(2)

    with col1:
        lite_mode = st.checkbox("Lite Mode", value=False)
        skip_tree = st.checkbox("Skip Directory Tree", value=False)
        sync_ignore = st.checkbox("Use .gittxtignore", value=False)
        docs_only = st.checkbox("Docs Only", value=False)

    with col2:
        txt = st.checkbox(".txt", value=True)
        md = st.checkbox(".md", value=True)
        json = st.checkbox(".json", value=True)
        zip_bundle = st.checkbox("Create ZIP Bundle", value=False)

    selected_formats = [fmt for fmt, checked in zip(["txt", "md", "json"], [txt, md, json]) if checked]

    return lite_mode, skip_tree, sync_ignore, docs_only, selected_formats, zip_bundle


def format_number_k(num):
    """Format a number with 'K' for thousands, 'M' for millions, etc."""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return str(num)


def render_scan_result(result):
    if result.get("error"):
        st.error(result["error"])
        return

    st.success(f"✅ Scan complete for {result['repo_name']}")

    st.subheader("📊 Repository Summary")
    summary = result["summary"]
    col1, col2 = st.columns([0.6, 0.4])

    with col1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Files", summary["total_files"])
        c2.metric("Total Size", humanize.naturalsize(summary["total_size"]))
        c3.metric("Estimated Tokens", format_number_k(summary['estimated_tokens']))

        st.markdown("### 🔍 Tokens by Type")
        token_table = summary.get("tokens_by_type", {})
        if token_table:
            df = pd.DataFrame({
                "Type": list(token_table.keys()),
                "Tokens": [format_number_k(v) for v in token_table.values()]
            })
            st.dataframe(df.style.set_properties(**{'text-align': 'center'}).hide(axis="index"), use_container_width=True)

    with col2:
        if result.get("skipped"):
            with st.expander("⚠️ Skipped Files"):
                for path, reason in result["skipped"]:
                    st.markdown(f"- `{path}` → *{reason}*")

    st.subheader("📄 Download Outputs")
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        for path in result["output_files"]:
            p = Path(path)
            st.download_button(
                label=f"⬇️ {p.name}",
                data=p.read_bytes(),
                file_name=p.name,
                mime="application/octet-stream",
            )
    with col2:
        if result.get("non_textual"):
            with st.expander("🎨 Non-Textual Assets Included"):
                for a in result["non_textual"]:
                    st.markdown(f"- `{a}`")
