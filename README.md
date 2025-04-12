🚀 **AI-Ready Text Extractor for Git Repos** | CLI tool for dataset prep, summaries, reverse engineering & bundling

# 📝 Gittxt: Get text from Git repositories in AI-ready formats

[![Docs](https://img.shields.io/badge/docs-online-blue?logo=mkdocs&labelColor=gray)](https://sandy-sp.github.io/gittxt/)
[![Python Version](https://img.shields.io/badge/python-≥3.8-blue)](pyproject.toml)
[![PyPI version](https://badge.fury.io/py/gittxt.svg)](https://pypi.org/project/gittxt/)
[![Release](https://img.shields.io/github/release/sandy-sp/gittxt.svg)](https://github.com/sandy-sp/gittxt/releases)
[![Tested with Pytest](https://img.shields.io/badge/tested%20with-pytest-9cf.svg)](https://docs.pytest.org/en/stable/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/gittxt)](https://pypi.org/project/gittxt/)
![GitHub repo size](https://img.shields.io/github/repo-size/sandy-sp/gittxt)
![GitHub top language](https://img.shields.io/github/languages/top/sandy-sp/gittxt)
[![Build Status](https://github.com/sandy-sp/gittxt/actions/workflows/release.yml/badge.svg)](https://github.com/sandy-sp/gittxt/actions)
[![Made for LLMs](https://img.shields.io/badge/LLM%20ready-Yes-brightgreen)](https://github.com/sandy-sp/gittxt)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ✨ What is Gittxt? 
![](./docs/getting-started/assets/gittxt-demo.gif)

**Gittxt** is a powerful CLI and plugin framework that extracts structured text and metadata from Git repositories. It’s designed to help you build AI-ready datasets, analyze large codebases, and even reverse engineer report outputs.

Use it for:
- 🔍 Curating datasets from code and documentation
- 🗃️ Generating `.txt`, `.json`, `.md`, and `.zip` bundles
- 📑 Extracting and classifying technical files by sub-type
- 🧠 Analyzing size, token count, and file types
- 🔄 Reconstructing full project trees from summary reports

---

## 🚀 Features

- ✅ **File-Type Detection** (extension, MIME, content heuristic)
- ✅ **.gittxtignore Support** (with `--sync`)
- ✅ **Subcategory Classification** (docs, config, code, etc.)
- ✅ **Async File I/O** for scalable performance
- ✅ **Lite Mode** for minimal outputs (`--lite`)
- ✅ **Bundled ZIPs** (`--zip`) with manifest, summary, README
- ✅ **Reverse Engineering** from `.txt`, `.md`, `.json` reports
- ✅ **Plugin System**: `gittxt-api`, `gittxt-streamlit`, etc.

---

## 🏗️ Installation

```bash
pip install gittxt
```

Or for development:

```bash
git clone https://github.com/sandy-sp/gittxt.git
cd gittxt
poetry install
poetry run gittxt config install  # Optional installer
```

---

## ⚙️ Quickstart

```bash
gittxt scan https://github.com/sandy-sp/gittxt --output-format txt,json --zip --lite
gittxt re outputs/gittxt_summary.json
```

---

## 🖥️ CLI Commands

```bash
gittxt scan [OPTIONS] [REPOS]...
gittxt config [SUBCOMMANDS]
gittxt clean [--output-dir]
gittxt re REPORT_FILE [--output-dir]
gittxt plugin [list|install|run|uninstall]
```

---

## 🔌 Plugin System

```bash
gittxt plugin list
gittxt plugin install gittxt-api
gittxt plugin run gittxt-api
```

Plugins include:

- 🧪 `gittxt-api`: FastAPI backend for scanning and summaries
- 🖥️ `gittxt-streamlit`: Interactive visual dashboard

---

## 📦 Output Formats

```
<output_dir>/
├── txt/
├── json/
├── md/
├── zip/
│   ├── summary.json
│   ├── manifest.json
│   ├── outputs/
│   └── assets/
```

---

## 🔄 Reverse Engineer

```bash
gittxt re report.txt -o ./restored
```

This recreates original file structure in a ZIP from Gittxt `.txt`, `.md`, or `.json` reports.

---

## 📚 Documentation

Docs are now organized in a full [MkDocs site](https://your-docs-site-url.com) with:

- ✅ Getting Started
- ✅ CLI Reference
- ✅ API Endpoints
- ✅ Reverse Engineering
- ✅ Developer & Contributor Guide

---

## 🛣️ Roadmap

- ✅ Plugin framework with API/Streamlit
- ✅ Reverse from Gittxt reports
- ⏳ AI-powered summaries
- ⏳ Live web UI

---

## 🤝 Contributing

See [Contributing Guide](https://your-docs-site-url.com/development/contributing)

```bash
make lint     # Code style
make test     # Run CLI + API tests
```

---

## 🛡️ License

MIT License © [Sandeep Paidipati](https://github.com/sandy-sp)

---

Gittxt — **Get text from Git repositories in AI-ready formats.**
