# 🚀 Gittxt: Get Text from Git — Optimized for AI

**Gittxt** is an open-source tool that transforms GitHub repositories into LLM-compatible datasets.

Perfect for developers, data scientists, and AI engineers, Gittxt helps you extract and structure `.txt`, `.json`, `.md` content into clean, analyzable formats for use in:
- Prompt engineering
- Fine-tuning & retrieval
- Codebase summarization
- Open-source LLM workflows

---

## 💡 Why Gittxt?
Large Language Models often expect input in very specific formats. Many tools (e.g., ChatGPT, Gemini, Ollama) struggle with arbitrary GitHub URLs, complex folders, or non-text assets.

Gittxt bridges this gap by:
- Extracting **all usable text** from a repo
- Organizing it for **easy ingestion by LLMs**
- Offering **structured `.txt`, `.json`, `.md`, `.zip` outputs**
- Giving you full control with filtering, formatting, and plugin support

---

## ✨ Features at a Glance
- ✅ Text extractor for code, docs, config files
- ✅ Output: `.txt`, `.json`, `.md`, `.zip`
- ✅ CLI and plugin system (FastAPI, Streamlit)
- ✅ AI-ready summaries (OpenAI / Ollama)
- ✅ Reverse engineer `.txt`/`.json` reports back into repo structure
- ✅ `.gittxtignore` support
- ✅ Async scanning for large projects
- ✅ Works offline and in constrained compute environments

---

## 📁 Output Types
```text
outputs/
├── txt/         # Plain text report
├── json/        # Structured metadata
├── md/          # Markdown-formatted summary
└── zip/         # Bundled results + manifest
```

---

## 🚀 Quickstart

### Install
```bash
pip install gittxt
```

### Run your first scan
```bash
gittxt scan https://github.com/sandy-sp/gittxt --output-format txt,json --lite --zip
```

### Reverse engineer a summary
```bash
gittxt re outputs/project.md -o ./restored
```

---

## 🌐 Explore the Visual Web App
Try the hosted version (no install required!)

👉 [Launch Streamlit App](https://gittxt.streamlit.app/)

---

## 📈 Gittxt for AI Workflows
- Use it to build structured input for LLMs
- Ideal for **prompt chaining**, **document agents**, **code summarization**
- Helps transform messy repos into single-file, AI-consumable reports

---

## 📖 Full Documentation
All CLI flags, plugins, formats, and filters are documented here:

📚 [Explore Gittxt Docs](https://sandy-sp.github.io/gittxt/)

---

## 🔧 Plugin Support
Gittxt supports modular plugins:

- `gittxt-api`: Run via FastAPI backend
- `gittxt-streamlit`: Interactive dashboard

Install & run with:
```bash
gittxt plugin install gittxt-streamlit
gittxt plugin run gittxt-streamlit
```

---

## 🧠 Built for Developers & AI Engineers
Created by [Sandeep Paidipati](https://www.linkedin.com/in/sandeep-paidipati), Gittxt was born out of a need to:
- Quickly preview and summarize GitHub repos with LLMs
- Avoid manual copying, filtering, and converting files
- Create AI-ready datasets for learning and experimentation

---

## 🙏 Support the Project
- ⭐️ Star [this repo](https://github.com/sandy-sp/gittxt) if it helped you
- 🧵 Share it with your dev/AI community
- 🤝 Contact me for collaboration or sponsorship

---

## 🔒 License
MIT License © [Sandeep Paidipati](https://github.com/sandy-sp)

---

**Gittxt** — **Get Text from Git — Optimized for AI**

