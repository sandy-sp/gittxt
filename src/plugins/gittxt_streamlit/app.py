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

st.set_page_config(page_title="Gittxt Streamlit Plugin", layout="wide")
st.title("🧾 Gittxt: Scan GitHub Repos to Text")

if "scan_result" not in st.session_state:
    st.session_state.scan_result = None

# --- Main UI Input ---
st.subheader("📥 Enter GitHub Repository URL")
repo_url = st.text_input("GitHub URL or Local Path", placeholder="https://github.com/user/repo")

st.subheader("🧩 Filter Settings")
include_patterns, exclude_patterns, exclude_dirs, size_limit, tree_depth = section_filters()

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
