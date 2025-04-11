import streamlit as st
import subprocess
import shutil
from pathlib import Path
import json

# Constants
OUTPUT_DIR = Path("plugin_output")
SUBDIRS = ["txt", "json", "md", "zip"]

# --- Session State Setup ---
if "scan_complete" not in st.session_state:
    st.session_state.scan_complete = False
if "scan_output_path" not in st.session_state:
    st.session_state.scan_output_path = None

# --- UI Header ---
st.set_page_config(page_title="Gittxt Streamlit", layout="wide")
st.title("📦 Gittxt – GitHub Repo to AI-Ready Text")

col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔁 Restart / Clear Output"):
        try:
            if OUTPUT_DIR.exists():
                shutil.rmtree(OUTPUT_DIR)
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # recreate empty
        except Exception as e:
            st.error(f"Failed to clear output: {e}")

        st.session_state.clear()
        st.rerun()

# === If Scan Already Complete, Load Results ===
if st.session_state.scan_complete and st.session_state.scan_output_path:
    OUTPUT_DIR = Path(st.session_state.scan_output_path)
    st.success("✅ Scan complete!")

    # Show summary
    json_dir = OUTPUT_DIR / "json"
    json_files = list(json_dir.glob("*.json"))
    if json_files:
        summary_file = json_files[0]
        with summary_file.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                st.subheader("📊 Scan Summary")
                repo = data.get("repository", {})
                summ = data.get("summary", {})
                st.markdown(f"**Repo**: `{repo.get('name')}`  \n**Branch**: `{repo.get('branch')}`")
                st.markdown(f"**Total Files**: `{summ.get('total_files')}`  \n**Estimated Tokens**: `{summ.get('formatted', {}).get('estimated_tokens')}`")
                st.markdown("**Directory Tree**:")
                st.code(repo.get("tree_summary", ""), language="text")
            except Exception as e:
                st.warning(f"⚠️ Failed to parse summary: {e}")

    # Preview Files (Lite only)
    if data and data.get("files"):
        st.subheader("📁 Preview Textual Files")
        for f in data["files"][:10]:  # limit preview
            with st.expander(f"📝 {f['path']}"):
                st.code(f['content'], language="text")

    # Download buttons
    st.subheader("📥 Download Outputs")
    for sub in SUBDIRS:
        subdir = OUTPUT_DIR / sub
        if subdir.exists():
            for file in subdir.glob("*.*"):
                st.download_button(
                    label=f"⬇️ {file.name}",
                    data=file.read_bytes(),
                    file_name=file.name,
                    mime="application/octet-stream",
                    key=f"dl-{file.name}"
                )
    st.stop()  # prevents re-render of input area after scan

# === SCAN UI (shown only when not already scanned) ===
# Pre-scan check
if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
    st.warning("⚠️ Output directory is not empty. Please restart before a new scan.")
    st.stop()

# GitHub input form
github_url = st.text_input("Enter a GitHub repository URL", placeholder="https://github.com/user/repo")

with st.expander("⚙️ Optional Flags"):
    lite = st.checkbox("Lite Mode", value=False)
    zip_bundle = st.checkbox("Include ZIP Output", value=False)
    output_format = st.multiselect("Output Format", ["txt", "json", "md"], default=["txt"])

run_button = st.button("🚀 Run Gittxt Scan")

if run_button and github_url:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        "gittxt", "scan", github_url,
        "-o", str(OUTPUT_DIR),
        "-f", ",".join(output_format)
    ]
    if lite:
        cmd.append("--lite")
    if zip_bundle:
        cmd.append("--zip")

    with st.spinner("🧠 Running Gittxt scan..."):
        result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stderr:
        st.error(result.stderr)
    else:
        st.session_state.scan_complete = True
        st.session_state.scan_output_path = str(OUTPUT_DIR)
        st.rerun()
