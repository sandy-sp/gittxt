> 🚀 **LLM Dataset Extractor from GitHub Repos** | AI & NLP-ready text pipelines

# 📝 Gittxt: Get text from Git repositories in AI-ready formats

[![Python Version](https://img.shields.io/badge/python-≥3.8-blue)](pyproject.toml)
[![PyPI version](https://badge.fury.io/py/gittxt.svg)](https://pypi.org/project/gittxt/)
[![Release](https://img.shields.io/github/release/sandy-sp/gittxt.svg)](https://github.com/sandy-sp/gittxt/releases)
[![Tested with Pytest](https://img.shields.io/badge/tested%20with-pytest-9cf.svg)](https://docs.pytest.org/en/stable/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/gittxt)](https://pypi.org/project/gittxt/)
![GitHub repo size](https://img.shields.io/github/repo-size/sandy-sp/gittxt)
![GitHub top language](https://img.shields.io/github/languages/top/sandy-sp/gittxt)
[![Build Status](https://github.com/sandy-sp/gittxt/actions/workflows/release.yml/badge.svg)](https://github.com/sandy-sp/gittxt/actions)
[![Made for LLMs](https://img.shields.io/badge/LLM%20ready-Yes-brightgreen)](https://github.com/sandy-sp/gittxt)
[![Linted with Ruff](https://img.shields.io/badge/linter-ruff-%23007ACC.svg)](https://github.com/charliermarsh/ruff)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

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

- ✅ **Dynamic File-Type Filtering** (based on extension + MIME + content heuristics)
- ✅ **Smart Directory Tree Summaries** with configurable depth and excludes
- ✅ **Multiple Output Formats**: `.txt`, `.json`, `.md`, `.zip`
- ✅ **Lite Mode** (`--lite`) for fast, minimal reports
- ✅ **ZIP Bundling** with `--zip` including `summary.json` and assets
- ✅ **Rich Summary Tables** with size, tokens, and file breakdowns
- ✅ **.gittxtignore** support for per-repo custom exclusion
- ✅ **Async I/O and CLI Progress Bars** for performance and UX

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
gittxt scan https://github.com/sandy-sp/gittxt.git --output-format txt,json --zip --lite
```

👉 This will:
- Scan the repository root
- Output `.txt` + `.json` summary files
- Bundle them in a ZIP

For more real-world usage: [Usage Examples →](docs/USAGE_EXAMPLES.md)

---

## 🖥️ CLI Usage

```bash
gittxt scan [REPOS]... [OPTIONS]
```

### Common Flags
| Option | Description |
|--------|-------------|
| `--include-patterns` | Glob to include (e.g., `*.py`, `docs/**/*.md`) |
| `--exclude-patterns` | Glob to exclude (e.g., `tests/`, `*.zip`) |
| `--size-limit`       | Skip files larger than N bytes |
| `--branch`           | Use a specific branch for remote repos |
| `--zip`              | Create a bundled ZIP archive |
| `--lite`             | Minimal output without full content |
| `--output-dir`       | Where to write outputs |
| `--output-format`    | txt, json, md, or comma-separated list |

Run `gittxt scan --help` for the full CLI reference.

---

## 📦 Output Formats

Each scan produces structured outputs:

```text
<output_dir>/
├── text/              # .txt
├── json/              # .json
├── md/                # .md
└── zips/              # .zip (optional)
```

See [Formats Guide →](docs/FORMATS.md)

---

## 🛠 How It Works

1. 🔗 Clone repo (supports GitHub, local, subdirs)
2. 🌲 Walk files with exclusion rules and MIME checks
3. 📑 Classify files as TEXTUAL or NON-TEXTUAL
4. 📄 Format text files to `.txt`, `.json`, `.md`
5. 📦 Zip outputs and assets (optional)
6. 🧹 Remove temp files (stateless design)

---

## 🧪 Running Tests

```bash
make test
```

- Generates a test repo with multiple edge cases
- Runs full suite with Pytest
- Cleans up outputs

Test docs → [tests/README.md](tests/README.md)

---

## 📄 Configuration

- Override via CLI flags
- Or set env vars like `GITTXT_OUTPUT_DIR`
- `.gittxtignore` works like `.gitignore`

Advanced setup → [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

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
- ✅ Async file scanning
- ✅ ZIP archive export with manifest
- ✅ Lite mode output
- ⏳ AI-powered summaries (GPT, Claude)
- ⏳ YAML + CSV output support
- ⏳ Web UI via FastAPI

---

## 📄 License
MIT License © [Sandeep Paidipati](https://github.com/sandy-sp)

---

Gittxt — **Get text from Git repositories in AI-ready formats.**
