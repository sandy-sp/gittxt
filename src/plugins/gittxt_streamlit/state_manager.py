import streamlit as st
from pathlib import Path
import shutil

PLUGIN_OUTPUT_DIR = Path("/tmp/gittxt_plugin_output")


def init_session_state():
    """
    Initialize Streamlit session state variables.
    Avoid storing non-serializable objects.
    """
    default_keys = ["repo_info", "outputs", "filters_used"]
    for key in default_keys:
        if key not in st.session_state:
            st.session_state[key] = None

    # Ensure output directory exists
    if not PLUGIN_OUTPUT_DIR.exists():
        PLUGIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def clear_session_and_outputs():
    """
    Reset session state and clean the plugin output directory.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key]

    if PLUGIN_OUTPUT_DIR.exists():
        try:
            shutil.rmtree(PLUGIN_OUTPUT_DIR)
        except Exception:
            pass
    PLUGIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_output_dir() -> Path:
    """
    Return the plugin output directory path.
    """
    return PLUGIN_OUTPUT_DIR.resolve()
