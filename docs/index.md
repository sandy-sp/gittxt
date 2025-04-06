# 📝 Gittxt: AI-Ready Text Extractor for Git Repositories

[![PyPI](https://img.shields.io/pypi/v/gittxt)](https://pypi.org/project/gittxt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/sandy-sp/gittxt/blob/main/LICENSE)
[![CI](https://github.com/sandy-sp/gittxt/actions/workflows/release.yml/badge.svg)](https://github.com/sandy-sp/gittxt/actions)
[![Downloads](https://img.shields.io/pypi/dm/gittxt)](https://pypi.org/project/gittxt/)

---

**Gittxt** is a powerful and modular CLI tool that transforms Git repositories into clean, structured, and AI-ready datasets. Whether you're training a language model, conducting code analysis, or building a research corpus — Gittxt gives you the right tools to extract textual intelligence from any repo.

--

## 🚀 Key Features

=== "🧠 Intelligent Filtering"
    - Auto-detects textual files using extensions, MIME types, and content sampling
    - Supports `.gittxtignore`, glob filters, and CLI options for precision

=== "📦 Multiple Output Formats"
    - Extracts content to `.txt`, `.json`, `.md`
    - Full or minimal `--lite` mode output
    - Optional ZIP bundles with manifest and asset metadata

=== "🔄 Reverse Engineering"
    - Restore original code files from `.txt`, `.md`, or `.json` reports
    - Reconstructs directory tree and outputs a ZIP archive
    - Supports programmatic reuse of Gittxt outputs

=== "⚡ Fast & Async"
    - Fully asynchronous file I/O for high-speed scans
    - Optimized for both small projects and large monorepos

=== "🌐 GitHub Support"
    - Clone and scan GitHub repositories by URL
    - Supports `--branch` and `--subdir` for fine-grained control

---

## 🎯 What Can You Use Gittxt For?

- 🧬 **LLM Training Data** — curate datasets from code, docs, and markdown.
- 📑 **Project Summarization** — get token counts, file-type breakdowns, and directory trees.
- 📦 **Documentation Packaging** — bundle outputs and assets for downstream pipelines.
- 🧠 **AI Corpus Generation** — convert entire repos into standardized textual formats.

!!! tip "Supports Local & Remote Repos"
    Run scans on:
    
    - Local folders (`.` or path)
    - Remote GitHub repos (`https://github.com/...`)
    - Specific branches and subdirectories

---

## 📷 Demo

![Gittxt Demo](assets/gittxt-demo.gif)

---

## 📦 Install Gittxt

=== "📌 With pip (recommended)"
    ```bash
    pip install gittxt
    ```

=== "🐍 With Poetry (local development)"
    ```bash
    git clone https://github.com/sandy-sp/gittxt.git
    cd gittxt
    poetry install
    poetry run gittxt install
    ```

---

## 🚀 Quickstart Example

```bash
gittxt scan https://github.com/sandy-sp/gittxt --output-format txt,json --zip --lite
```

🧾 This will:
- Scan the `main` branch of the GitHub repo
- Generate `.txt` and `.json` summaries
- Bundle them with a manifest into a ZIP archive

---

## 📚 Explore the Docs

- 🔧 [Getting Started](getting-started.md)
- 🧪 [Usage Guide](usage.md)
- ⚙️ [Configuration Reference](configuration.md)
- 📘 [Output Formats](formats.md)
- 🧠 [API Reference](api-reference.md)
- 🛠 [Contributing](contributing.md)
- 🔁 [Reverse Engineering](reverse_engineer.md)

---

## 🛣 Roadmap

✅ Async file scanning  
✅ ZIP archive bundling  
✅ `.gittxtignore` support  
✅ Lite output mode  
⏳ AI-powered summaries (GPT, Claude)  
⏳ Web UI with FastAPI  
⏳ YAML + CSV outputs  

---

## 🤝 Join the Community

📬 [Submit Issues](https://github.com/sandy-sp/gittxt/issues)  
🤖 [Contribute on GitHub](https://github.com/sandy-sp/gittxt)  
💬 [Discuss Ideas](https://github.com/sandy-sp/gittxt/discussions)

---

Made with ❤️ by [Sandeep Paidipati](https://github.com/sandy-sp) • MIT Licensed

---
