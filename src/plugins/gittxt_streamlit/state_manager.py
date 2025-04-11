import streamlit as st
from pathlib import Path
import shutil

PLUGIN_OUTPUT_DIR = Path("/tmp/gittxt_plugin_output")


def init_session_state():
    """
    Initialize Streamlit session state variables.
    """
    if "repo_info" not in st.session_state:
        st.session_state["repo_info"] = None
    if "outputs" not in st.session_state:
        st.session_state["outputs"] = None
    if not PLUGIN_OUTPUT_DIR.exists():
        PLUGIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clear_session_and_outputs():
    """
    Reset session state and delete all outputs.
    """
    st.session_state.clear()
    if PLUGIN_OUTPUT_DIR.exists():
        shutil.rmtree(PLUGIN_OUTPUT_DIR)
        PLUGIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
