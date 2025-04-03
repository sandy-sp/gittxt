> 🚀 **AI-Ready Text Extractor for Git Repos** | CLI tool for dataset prep, summaries & bundling

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
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ✨ What is Gittxt?
![](./docs/gittxt-demo.gif)

**Gittxt** is a modular and configurable CLI tool that converts Git repositories into clean, AI-ready textual datasets. It is built for developers, researchers, and ML engineers who need structured, filtered, and summarized content from codebases and technical documentation.

With support for smart file classification, flexible exclusion logic, and multiple output formats, Gittxt is a versatile tool for:

- 🔍 Curating LLM training data from source code
- 🗃️ Converting repos into structured `.txt`, `.json`, `.md`, and `.zip` outputs
- 📑 Extracting docs, comments, and markdown files from large monorepos
- 🧠 Analyzing repositories by token counts, file size, and content types
- 📦 Bundling outputs for reproducibility and downstream pipelines

It supports both local folders and GitHub URLs with branch/subdir targeting.

---

## 🚀 Features

- ✅ **Dynamic File-Type Filtering** (extension + MIME + content heuristics)
- ✅ **Smart Directory Tree Summaries** with depth and exclude support
- ✅ **Multiple Output Formats**: `.txt`, `.json`, `.md`, `.zip`
- ✅ **Lite Mode** (`--lite`) for fast, minimal reports
- ✅ **ZIP Bundling** with `--zip`, including `summary.json`, `manifest.json`, and assets
- ✅ **Rich Summary Tables** with size, token, and type breakdowns
- ✅ **.gittxtignore** support for repo-specific exclusions
- ✅ **Async File I/O** for efficient scanning

---

## 🏗️ Installation

### 🐍 Using pip (stable)

```bash
pip install gittxt
```

### 📦 Using Poetry

```bash
git clone https://github.com/sandy-sp/gittxt.git
cd gittxt
poetry install
# Optional Gittxt setup
poetry run gittxt install
```
---

## ⚙️ Quickstart Example

```bash
gittxt scan https://github.com/sandy-sp/gittxt.git --output-format txt,json --zip --lite
```

👉 This will:

- Scan the repository root
- Output `.txt` and `.json` summary files
- Bundle outputs in a ZIP with manifest and summary

More examples → [Usage Examples](docs/USAGE_EXAMPLES.md)

---

## 🖥️ CLI Usage

```bash
gittxt scan [OPTIONS] [REPOS]...
```

📦 Scan directories or GitHub repos (textual only).

### Options

| Option                                      | Description                                     |
| ------------------------------------------- | ----------------------------------------------- |
| `-x`, `--exclude-dir`                       | Exclude folder paths                            |
| `-o`, `--output-dir PATH`                   | Custom output directory                         |
| `-f`, `--output-format TEXT`                | Comma-separated: txt, json, md                  |
| `-i`, `--include-patterns TEXT`             | Glob to include (only textual)                  |
| `-e`, `--exclude-patterns TEXT`             | Glob to exclude                                 |
| `--zip`                                     | Create a ZIP bundle                             |
| `--lite`                                    | Generate minimal output instead of full content |
| `--sync`                                    | Opt-in to .gitignore usage                      |
| `--size-limit INTEGER`                      | Max file size in bytes                          |
| `--branch TEXT`                             | Git branch for remote repos                     |
| `--tree-depth INTEGER`                      | Limit tree output to N levels                   |
| `--log-level [debug\|info\|warning\|error]` | Set log verbosity level                         |
| `--help`                                    | Show CLI help and exit                          |

Run `gittxt scan --help` for the full reference.

---

## 📦 Output Formats

Each scan produces structured outputs:

```text
<output_dir>/
├── text/              # .txt
├── json/              # .json
├── md/                # .md
├── zips/              # .zip (optional)
│   └── manifest.json, summary.json, outputs/, assets/
```

See [Formats Guide](docs/FORMATS.md)

---

## 🛠 How It Works

1. 🔗 Clone repo (local or GitHub, with branch/subdir support)
2. 🌲 Walk repo with filtering and MIME rules
3. 📑 Classify TEXTUAL vs NON-TEXTUAL
4. 📝 Format output to `.txt`, `.json`, `.md`
5. 📦 Bundle ZIP with summary + manifest (optional)
6. 🧹 Clean temp state after scan

---

## 🧰 Gittxt Installer

Run the interactive installer to configure Gittxt preferences:

```bash
gittxt config install
```

This command lets you:

- Set default **output directory** and **formats** (txt/json/md)
- Configure **log level** (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- Enable or disable automatic **ZIP bundling**
- Define or override:
  - Textual extensions (e.g. `.py`, `.md`)
  - Non-textual extensions (e.g. `.png`, `.zip`)
  - Excluded directories (e.g. `.git`, `node_modules`)

The config is saved to `gittxt-config.json` and used as default for all scans.

---

## 📄 Configuration

- CLI flags (e.g., `--output-dir`, `--size-limit`)
- Environment variables (e.g., `GITTXT_OUTPUT_DIR`)
- `.gittxtignore` file support for exclusions

Config details → [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

---

## 🔐 Security Policy

Please report security issues to: [**sandeep.paidipati@gmail.com**](mailto\:sandeep.paidipati@gmail.com)\
[Security Guidelines](docs/SECURITY.md)

---

## 🤝 Contributing

We welcome contributions from the community!

- [Contributing Guide](docs/CONTRIBUTING.md)
- [Code of Conduct](docs/CODE_OF_CONDUCT.md)
- [Open Issue](https://github.com/sandy-sp/gittxt/issues/new/choose)

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

