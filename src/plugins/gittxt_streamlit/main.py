import streamlit as st
from scan import app as scan_app
from ai_summary import run_ai_summary_ui

st.set_page_config(page_title="Gittxt App", layout="wide")
st.sidebar.title("🔀 Gittxt Navigation")

page = st.sidebar.radio("Go to", ["📂 Scan Repository", "🧠 AI Repo Summary"])

if page == "📂 Scan Repository":
    scan_app.run_scan_ui()
elif page == "🧠 AI Repo Summary":
    run_ai_summary_ui()
