import streamlit as st
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
)  # Removed display_download_button
from plugins.gittxt_streamlit.state_manager import init_session_state

st.set_page_config(page_title="Gittxt Streamlit", layout="wide")
init_session_state()

st.title("🧠 Gittxt: GitHub Repo Scanner & Formatter")

# --- Phase 1: GitHub Repo URL Input ---
with st.form("repo_input_form"):
    github_url = st.text_input("Enter a GitHub Repository URL", placeholder="https://github.com/sandy-sp/gittxt")
    col1, col2 = st.columns([9, 1])
    with col1:
        include_default_excludes = st.checkbox(
            "Include Default Excluded Directories", value=True, key="default_excludes_checkbox"
        )
    with col2:
        display_hidden_icon_with_tooltip()  # Add the hidden icon with tooltip
    include_gitignore = st.checkbox(
        "Include .gitignore Rules", value=True, key="gitignore_checkbox"
    )
    submitted = st.form_submit_button("Inspect Repository")

if submitted and github_url:
    with st.spinner("Cloning and analyzing repository..."):
        repo_info = load_repository_summary(
            github_url,
            include_default_excludes=include_default_excludes,
            include_gitignore=include_gitignore
        )
        if repo_info:
            st.session_state["repo_info"] = repo_info
            st.success("Repository loaded successfully!")
        else:
            st.error("Failed to clone or inspect repository.")

# --- Phase 2: Display Summary & Filters ---
repo_info = st.session_state.get("repo_info")
if repo_info:
    col1, col2 = st.columns([1, 1])
    with col1:
        display_summary(repo_info)
    with col2:
        display_directory_tree(repo_info)

    st.markdown("---")
    st.subheader("🔧 Configure Scan Filters")
    with st.form("filters_form"):
        filters = display_filter_form(repo_info)
        run_scan = st.form_submit_button("Run Scan")

    # Removed the call to display_download_button
    # if filters:
    #     display_download_button(filters)

    if run_scan:
        with st.spinner("Running filtered scan..."):
            output_paths = execute_scan_with_filters(github_url, filters)
            st.session_state["outputs"] = output_paths
            st.success("Scan complete. You can now download the outputs.")

# --- Phase 3: Display and Download Results ---
if st.session_state.get("outputs"):
    display_outputs(st.session_state["outputs"])
    if st.button("Restart & Clean Output"):
        cleanup_output_dir()
        st.session_state.clear()
        st.rerun()
