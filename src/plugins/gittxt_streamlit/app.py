# src/plugins/gittxt_streamlit/app.py

import streamlit as st
import asyncio
from pathlib import Path
from pipeline import full_cli_equivalent_scan
from ui_components import (
    section_filters,
    section_options,
    render_scan_result,
)
from gittxt.core.constants import (
    DEFAULT_FILETYPE_CONFIG,
    EXCLUDED_DIRS_DEFAULT,
)

st.set_page_config(page_title="Gittxt Streamlit Plugin", layout="wide")
st.title("🧾 Gittxt: Scan GitHub Repos to Text")

if "scan_result" not in st.session_state:
    st.session_state.scan_result = None

# --- Main UI Input ---
st.subheader("📥 Enter GitHub Repository URL")
repo_url = st.text_input("GitHub URL or Local Path", placeholder="https://github.com/user/repo")

# --- Filter Settings Section with Toggle ---
col1, col2 = st.columns([0.9, 0.1])
with col1:
    st.subheader("🧩 Filter Settings")
with col2:
    use_defaults = st.toggle("Use Default Filter Settings", value=True, label_visibility="collapsed")

# --- Determine filter values ---
if use_defaults:
    include_patterns = ",".join(f"**/*{ext}" for ext in DEFAULT_FILETYPE_CONFIG["textual_exts"])
    exclude_patterns = ""
    exclude_dirs = ",".join(EXCLUDED_DIRS_DEFAULT)
    size_limit = 1_000_000
    tree_depth = 5

    with st.expander("🔍 Default Filter Preview", expanded=False):
        st.markdown("**Included Extensions:**")
        st.code(include_patterns, language="text")
        st.markdown("**Excluded Directories:**")
        st.code(exclude_dirs, language="text")
        st.markdown("**Max File Size:**")
        st.code(f"{size_limit} bytes", language="text")
        st.markdown("**Tree Depth:**")
        st.code(str(tree_depth), language="text")
else:
    include_patterns, exclude_patterns, exclude_dirs, size_limit, tree_depth = section_filters()

# --- Options Section ---
st.subheader("⚙️ Scan Options")
lite_mode, zip_bundle, skip_tree, sync_ignore, output_formats = section_options()

# --- Run Scan Button ---
if st.button("🚀 Run Scan", type="primary") and repo_url:
    with st.status("Running scan...", expanded=True):
        filters = {
            "branch": None,
            "subdir": None,
            "include_patterns": [p.strip() for p in include_patterns.split(",") if p.strip()],
            "exclude_patterns": [p.strip() for p in exclude_patterns.split(",") if p.strip()],
            "exclude_dirs": [d.strip() for d in exclude_dirs.split(",") if d.strip()],
            "size_limit": size_limit,
            "output_formats": output_formats,
            "output_dir": "/tmp/gittxt_streamlit_output",
            "lite": lite_mode,
            "zip": zip_bundle,
            "skip_tree": skip_tree,
            "tree_depth": tree_depth,
            "sync": sync_ignore,
        }
        result = asyncio.run(full_cli_equivalent_scan(repo_url, filters))
        st.session_state.scan_result = result

# --- Display Results ---
if st.session_state.scan_result:
    render_scan_result(st.session_state.scan_result)
