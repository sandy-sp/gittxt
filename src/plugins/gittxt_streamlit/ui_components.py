import streamlit as st
from pathlib import Path

def display_summary(repo_info: dict):
    summary = repo_info.get("summary", {})
    st.subheader("📊 Repository Summary")
    st.markdown(f"**Repo Name**: `{repo_info['repo_name']}`")
    st.markdown(f"**Total Files**: `{summary.get('total_files', 0)}`")
    st.markdown(f"**Estimated Tokens**: `{summary.get('formatted', {}).get('estimated_tokens', '-')}`")
    st.markdown(f"**Total Size**: `{summary.get('formatted', {}).get('total_size', '-')}`")


def display_directory_tree(repo_info: dict):
    st.subheader("🌲 Directory Tree")
    st.code(repo_info.get("dir_tree", "(No tree available)"), language="text")


def display_file_type_selector(repo_info: dict):
    st.subheader("📂 File Type Classification")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Textual Extensions (editable)**")
        textual = st.multiselect(
            "Select extensions to treat as textual:",
            options=sorted(repo_info.get("textual_types", [])),
            default=sorted(repo_info.get("textual_types", [])),
            key="textual_selector"
        )
    with col2:
        st.markdown("**Non-Textual Extensions (locked)**")
        st.write(", ".join(sorted(repo_info.get("non_textual_types", []))) or "-")

    return textual  # Return updated textual list for override


def display_filter_form(repo_info: dict):
    filters = {}
    filters["repo_path"] = repo_info["repo_path"]
    filters["scanner"] = repo_info["scanner"]

    # Exclude by directory (from tree)
    tree_lines = repo_info.get("dir_tree", "").split("\n")
    all_dirs = sorted({line.strip("│├└─ ") for line in tree_lines if "/" not in line and line.strip()})
    filters["exclude_dirs"] = st.multiselect("Exclude Directories:", all_dirs, key="exclude_dirs")

    filters["include_patterns"] = st.text_input("Include Patterns (comma-separated):", key="include_patterns").split(",")
    filters["exclude_patterns"] = st.text_input("Exclude Patterns (comma-separated):", key="exclude_patterns").split(",")

    # File type selector
    filters["custom_textual"] = display_file_type_selector(repo_info)

    # Size filter
    max_kb = 1000
    filters["size_limit"] = st.slider("Max File Size (KB):", min_value=1, max_value=max_kb, value=200) * 1024

    # Output format
    filters["output_formats"] = st.multiselect("Output Formats:", ["txt", "json", "md"], default=["txt"], key="formats")

    filters["lite_mode"] = st.checkbox("Lite Mode", value=False, key="lite")
    filters["zip_output"] = st.checkbox("Include ZIP Bundle", value=True, key="zip")

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
