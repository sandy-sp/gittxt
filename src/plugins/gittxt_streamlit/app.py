import streamlit as st
import subprocess
import tempfile
from pathlib import Path

st.set_page_config(page_title="Gittxt Streamlit", layout="wide")
st.title("📦 Gittxt – GitHub Repo to AI-Ready Text")

github_url = st.text_input("Enter a GitHub repository URL", placeholder="https://github.com/sandy-sp/gittxt")

with st.expander("⚙️ Optional Flags"):
    lite = st.checkbox("Lite Mode", value=False)
    zip_bundle = st.checkbox("Include ZIP Output", value=False)
    output_format = st.multiselect("Output Format", ["txt", "json", "md"], default=["txt"])

run_button = st.button("🚀 Run Gittxt Scan")

if run_button and github_url:
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir)
        cmd = [
            "gittxt",
            "scan",
            github_url,
            "-o", str(output_path),
            "-f", ",".join(output_format)
        ]
        if lite:
            cmd.append("--lite")
        if zip_bundle:
            cmd.append("--zip")

        st.write("🔍 Running scan...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        st.code(result.stdout, language="bash")
        if result.stderr:
            st.error(result.stderr)

        st.success("✅ Scan complete. Check your output folder.")
