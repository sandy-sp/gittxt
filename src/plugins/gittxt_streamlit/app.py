import streamlit as st
import asyncio

from plugins.gittxt_streamlit.pipeline import (
    load_repository_summary,
    execute_scan_with_filters,
    cleanup_output_dir
)
from plugins.gittxt_streamlit.ui_components import (
    display_summary,
    display_directory_tree,
    display_filter_form,
    display_outputs,
    display_hidden_icon_with_tooltip
)
from plugins.gittxt_streamlit.state_manager import init_session_state

st.set_page_config(page_title="Gittxt Streamlit", layout="wide")
init_session_state()

st.title("\U0001f9e0 Gittxt: GitHub Repo Scanner & Formatter")


def validate_github_url(url: str) -> bool:
    if not url.startswith("https://github.com/"):
        return False
    parts = url.replace("https://github.com/", "").split("/")
    return len(parts) >= 2


# --- Phase 1: GitHub Repo URL Input ---
with st.form("repo_input_form"):
    github_url = st.text_input("Enter a GitHub Repository URL", placeholder="https://github.com/sandy-sp/gittxt")
    col1, col2 = st.columns([9, 1])
    with col1:
        include_default_excludes = st.checkbox(
            "Include Default Excluded Directories", value=True, key="default_excludes_checkbox"
        )
    with col2:
        display_hidden_icon_with_tooltip()
    include_gitignore = st.checkbox(
        "Include .gitignore Rules", value=True, key="gitignore_checkbox"
    )
    submitted = st.form_submit_button("Inspect Repository")

if submitted:
    if not github_url:
        st.warning("\u26a0\ufe0f Please enter a GitHub URL.")
    elif not validate_github_url(github_url):
        st.error("\u274c Invalid or incomplete GitHub repo URL.")
    else:
        with st.spinner("Cloning and analyzing repository..."):
            try:
                repo_info = asyncio.run(
                    load_repository_summary(
                        github_url,
                        include_default_excludes=include_default_excludes,
                        include_gitignore=include_gitignore
                    )
                )
                st.session_state["repo_info"] = repo_info
                st.session_state.pop("outputs", None)
                st.success("\u2705 Repository loaded successfully!")
            except Exception as e:
                st.error(f"\ud83d\udeab Failed to inspect repository: {e}")

# --- Phase 2: Display Summary & Filters ---
repo_info = st.session_state.get("repo_info")
if repo_info:
    col1, col2 = st.columns([1, 1])
    with col1:
        display_summary(repo_info)
    with col2:
        display_directory_tree(repo_info)

    st.markdown("---")
    st.subheader("\U0001f527 Configure Scan Filters")
    with st.form("filters_form"):
        filters = display_filter_form(repo_info)
        run_scan = st.form_submit_button("Run Scan")

    if run_scan:
        with st.spinner("Running filtered scan..."):
            try:
                cleanup_output_dir()
                outputs = asyncio.run(execute_scan_with_filters(filters))
                st.session_state["outputs"] = outputs
                st.session_state["filters_used"] = filters
                st.success("\u2705 Scan complete. You can now download the outputs.")
            except Exception as e:
                st.error(f"\u274c Scan failed: {e}")

# --- Phase 3: Display and Download Results ---
if st.session_state.get("outputs"):
    display_outputs(st.session_state["outputs"])
    if st.button("Restart & Clean Output"):
        cleanup_output_dir()
        st.session_state.clear()
        st.rerun()
