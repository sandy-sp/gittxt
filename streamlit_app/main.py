import streamlit as st

# Prevent page config error in submodules
if not st.session_state.get("page_config_set"):
    st.set_page_config(page_title="Gittxt App", layout="wide")
    st.session_state["page_config_set"] = True

from scan import app as scan_app
from ai.ai_summary import run_ai_summary_ui

# --- Sidebar Style Override ---
st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        background-color: #000000;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Customization ---
st.sidebar.image("https://raw.githubusercontent.com/sandy-sp/gittxt/main/docs/images/logo/gittxt.png", width=180)

st.sidebar.markdown("## 🚀 Navigation")

if st.sidebar.button("📂 Scan Repository"):
    st.session_state.page = "scan"
if st.sidebar.button("🧠 AI Repo Summary"):
    st.session_state.page = "summary"

st.sidebar.markdown("""
<p style='margin-top: 10px; font-size: 16px;'>
    📘 Curious how this project works under the hood? 
    <a href='https://sandy-sp.github.io/gittxt/' target='_blank'>Check out the Gittxt Docs</a> for usage, features, and API details.
</p>
<p style='margin-top: 20px; font-size: 16px;'> 
    💡 Enjoying this project? Interested in building similar developer tools or collaborating on OSS?
    Let’s connect and share ideas!
</p>
<style>
.social-icons a {
    text-decoration: none;
    font-size: 20px;
    display: inline-flex;
    align-items: center;
    margin-right: 10px;
    margin-bottom: 6px;
}
.social-icons a:hover {
    text-decoration: underline;
}
</style>
<div class='social-icons'>
    <a href="https://www.linkedin.com/in/sandeep-paidipati" target="_blank">
        <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/linkedin.svg" width="24" style="margin-right:8px; vertical-align:middle; filter: invert(1);" /> LinkedIn
    </a><br>
    <a href="https://github.com/sandy-sp" target="_blank">
        <img src="https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/github.svg" width="24" style="margin-right:8px; vertical-align:middle; filter: invert(1);" /> GitHub
    </a>
</div>
""", unsafe_allow_html=True)

# --- Page Routing ---
page = st.session_state.get("page", "scan")

if page == "scan":
    scan_app.run_scan_ui()
elif page == "summary":
    run_ai_summary_ui()
