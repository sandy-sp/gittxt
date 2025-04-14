# main.py
import streamlit as st

# Prevent page config error in submodules
if not st.session_state.get("page_config_set"):
    st.set_page_config(page_title="Gittxt App", layout="wide")
    st.session_state["page_config_set"] = True

from scan import app as scan_app
from ai.ai_summary import run_ai_summary_ui

st.sidebar.title("🔀 Gittxt Navigation")
page = st.sidebar.radio("Go to", ["📂 Scan Repository", "🧠 AI Repo Summary"])

if page == "📂 Scan Repository":
    scan_app.run_scan_ui()
elif page == "🧠 AI Repo Summary":
    run_ai_summary_ui()
