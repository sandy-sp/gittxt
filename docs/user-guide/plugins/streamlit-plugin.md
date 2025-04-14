# 🌐 Gittxt Streamlit Plugin

The **Streamlit Plugin** provides a clean visual interface for Gittxt. It allows users to scan GitHub repositories and download AI-ready textual outputs via a local or cloud-hosted web app.

---

## 🚀 Launch the Web App

### Locally via CLI
```bash
gittxt plugin run gittxt-streamlit
```

### Or Manually
```bash
streamlit run src/plugins/gittxt_streamlit/main.py
```

App runs at: [http://localhost:8501](http://localhost:8501)

---

## ☁️ Hosted Version

Access the live app on **Streamlit Cloud**:
👉 [gittxt.streamlit.app](https://gittxt.streamlit.app/)

This version mirrors the full CLI functionality with a polished UX.

---

## 🎛 Features

### 📂 Scan GitHub Repos
- Input any **public GitHub repository URL**
- Configure filters: `include/exclude patterns`, directory filters, `.gittxtignore` support
- Set output options: `.txt`, `.json`, `.md`, `--lite`, `--zip`, `--tree-depth`
- View **summary metrics**, skipped files, and non-textual assets
- One-click downloads for all outputs (including ZIP bundle)

### 🧠 AI Repo Summary (Beta)
- Generate LLM-based repo summaries using OpenAI or Ollama
- Choose Docs-Only vs Full-File mode for context
- View token-aware context preview before analysis
- Interact via **multi-turn chat**
- Export chat history as `.json` or `.md`

---

## 📁 Output Directory Structure

By default, outputs are written to:
```bash
/tmp/gittxt_streamlit_output/
├── txt/
├── json/
├── md/
└── zip/
```

These are cleared when the **Restart** button is clicked.

---

## 🛠 Architecture Overview

The plugin is modular and mirrors the CLI tool:

```text
src/plugins/gittxt_streamlit/
├── main.py                # UI router (Scan ↔ AI Summary)
├── requirements.txt
├── scan/                  # Scan interface
│   ├── app.py             # Scan UI
│   ├── pipeline.py        # CLI-equivalent scanner logic
│   └── ui_components.py   # Filters, results, downloads
└── ai/                    # AI Summary interface
    ├── ai_summary.py      # Full LLM UI
    ├── llm_handler.py     # OpenAI / Ollama API calls
    ├── context_builder.py # Context builder from scanned files
    └── chat_exporter.py   # Export markdown / json chat
```

---

## ⚙️ Plugin Management

You can use the plugin CLI system to install and run this plugin:

### Install
```bash
gittxt plugin install gittxt-streamlit
```

### Run
```bash
gittxt plugin run gittxt-streamlit
```

Dependencies in `requirements.txt` are auto-installed on first run.

---

## ⚠️ Notes

- Scans call `gittxt scan` via internal async logic, mirroring CLI behavior.
- Only one scan can run per session. Restart clears prior output.
- Chat summary is experimental — LLM issues may occur (especially with token overflow).

---

## 💡 Tips

- Use **Docs-Only** mode for faster LLM summaries
- Toggle **Advanced Filters** to fine-tune file selection
- `.gittxtignore` is supported with the **Sync Ignore** checkbox
- Token counts and skipped file reasons are visible in the scan summary

---

Back: [API Plugin](api-plugin.md)

