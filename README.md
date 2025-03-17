# 📝 Gittxt: Get text from Git repositories in AI-ready formats.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-≥3.8-blue)](pyproject.toml)
[![Linted with Ruff](https://img.shields.io/badge/linter-ruff-%23007ACC.svg)](https://github.com/charliermarsh/ruff)
[![Tested with Pytest](https://img.shields.io/badge/tested%20with-pytest-9cf.svg)](https://docs.pytest.org/en/stable/)
[![Made for LLMs](https://img.shields.io/badge/LLM%20ready-Yes-brightgreen)](https://github.com/sandy-sp/gittxt)

---

## ✨ What is Gittxt?

**Gittxt** is a developer-focused CLI tool that extracts AI-ready text from **Git repositories**. Whether you're preparing datasets for **AI models**, **NLP pipelines**, or **LLM fine-tuning**, Gittxt automates the tedious task of repository scanning and text conversion.

Built with speed, flexibility, and modularity in mind, Gittxt is ideal for:
- Preparing **training data for LLMs** (e.g., ChatGPT, Claude, Mistral)
- **Documentation extraction** for knowledge bases
- **Code summarization** pipelines
- **Repository analysis** for machine learning workflows

---

## 🚀 Features

- ✅ **Dynamic File-Type Filtering** (`--file-types=code,docs,images,csv,media,all`)
- ✅ **Automatic Tree Generation** with clean filtering (excludes `.git/`, `__pycache__`, etc.)
- ✅ **Multiple Output Formats**: TXT, JSON, Markdown
- ✅ **Optional ZIP Packaging** for non-text assets
- ✅ **CLI-friendly Progress Bars**
- ✅ **Built-in Summary Reports** (`--summary`)
- ✅ **Interactive & CI-ready Modes** (`--non-interactive`)

---

## 🏗️ Installation

### 📦 Using Poetry
```bash
git clone https://github.com/sandy-sp/gittxt.git
cd gittxt
poetry install
poetry run gittxt install
```

### 🐍 Using pip (stable)
```bash
pip install gittxt
```

---

## ⚙️ Quickstart Example

```bash
gittxt scan https://github.com/user/repo.git --output-format txt,json --file-types code,docs --summary
```

👉 This will:
- Scan a GitHub repository
- Extract code & docs files
- Output `.txt` + `.json` summaries
- Show a summary report

---

## 🖥️ CLI Usage

```bash
gittxt scan [REPOS]... [OPTIONS]

Options:
  --include TEXT        Include patterns (e.g., *.py)
  --exclude TEXT        Exclude patterns (e.g., tests/, node_modules)
  --size-limit INTEGER  Max file size in bytes
  --branch TEXT         Specify branch (for GitHub URLs)
  --file-types TEXT     code, docs, images, csv, media, all
  --output-format TEXT  txt, json, md, or comma-separated list
  --output-dir PATH     Custom output directory
  --summary             Show post-scan summary
  --non-interactive     Skip prompts for CI/CD workflows
  --progress            Enable scan progress bars
  --debug               Enable debug logs
  --help                Show this message and exit
```

---

## 📂 Output Structure

```
<output_dir>/
├── text/
│   └── repo-name.txt
├── json/
│   └── repo-name.json
├── md/
│   └── repo-name.md
└── zips/
    └── repo-name_extras.zip  # Optional ZIP for assets (images, csv, etc.)
```

---

## 🛠 How It Works

1. 🔗 Clone GitHub/local repo (supports branch/subdir URLs)
2. 🌳 Dynamically generate directory tree (excluding `.git`, `__pycache__`, etc.)
3. 🗂️ Filter files based on type (code, docs, csv, media)
4. 📝 Generate formatted outputs (TXT, JSON, MD)
5. 📦 Package assets (optional ZIP for non-text)
6. 🧹 Cleanup temporary files (cache-free design)

---

## 📊 Example Summary Output

```
📊 Summary Report:
 - Total files processed: 45
 - Output formats: txt, json
 - File type breakdown: {'code': 31, 'docs': 14}
```

---

## 🔐 Security Policy
Please report security issues to: **sandeep.paidipati@gmail.com**  
[View Security Policy](docs/SECURITY.md)

---

## 🤝 Contributing
We welcome community contributions!  
- [Contributing Guidelines](docs/CONTRIBUTING.md)  
- [Code of Conduct](docs/CODE_OF_CONDUCT.md)  
- [Open an Issue](https://github.com/sandy-sp/gittxt/issues/new/choose)

---

## 🛣️ Roadmap
- FastAPI-powered web UI
- AI-powered summaries (GPT/OpenAI integration)
- Support YAML/CSV as additional output formats
- Async file scanning (speed boost)

---

## 📄 License
MIT License © [Sandeep Paidipati](https://github.com/sandy-sp)

---

Gittxt — **“Gittxt: Get text from Git repositories in AI-ready formats.”**

---