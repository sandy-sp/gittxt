# 📘 Welcome to Gittxt Docs

Gittxt is a command-line tool and plugin framework that converts Git repositories into clean, structured, AI-ready datasets.

Whether you're analyzing open source code, building training corpora, or archiving structured knowledge — Gittxt helps you:
- Extract textual content from repos with filters and format options
- Bundle outputs into `.txt`, `.json`, `.md`, or `.zip`
- Preview directory trees, token counts, and non-textual assets
- Extend functionality with plugins like a FastAPI backend or Streamlit UI

---

## 🎨 Try the Visual Web App

Want to understand how Gittxt works without installing anything?
Check out the hosted Streamlit app: 

➡️ [Try Gittxt on Streamlit Cloud](https://gittxt.streamlit.app/)

---

## 🚀 Quick Navigation

| Section | Description |
|--------|-------------|
| [Getting Started](getting-started/installation.md) | Install and run your first scan |
| [User Guide](user-guide/scanning.md) | Learn about configuration, filters, and outputs |
| [CLI Reference](cli-reference/index.md) | Full reference for all subcommands |
| [Plugin System](user-guide/plugins/index.md) | Streamlit + API plugin setup and usage |
| [API Reference](api-reference/index.md) | Endpoints and request/response structure |
| [Contributing](development/contributing.md) | For contributors and plugin developers |
| [Changelog](changelog.md) | See what’s new in each release |

---

## 💡 Key Features
- Modular CLI: `scan`, `config`, `plugin`, `re`, `clean`
- `.gittxtignore` support for gitignore-style filtering
- Lite vs Rich modes
- ZIP bundling and manifest/summary outputs
- Plugin system: FastAPI + Streamlit
- Hosted Streamlit app with full `gittxt scan` parity
- AI-Powered Summary & Chat (OpenAI / Ollama support)
- Fast, async scanning of large codebases

---

## 🌐 Join the Project
- GitHub: [github.com/sandy-sp/gittxt](https://github.com/sandy-sp/gittxt)
- Discussions: [Ask a question](https://github.com/sandy-sp/gittxt/discussions)
- Issues: [Report a bug](https://github.com/sandy-sp/gittxt/issues)

---

Let’s get started → [Installation Guide](getting-started/installation.md)

---

Want to know how Gittxt was born and why it exists?  
📖 [Read the full story → About Gittxt](about.md)
