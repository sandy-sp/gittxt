# 🚀 Gittxt: Get Text of Your Repo for AI, LLMs & Docs!

**Gittxt** is a fast, modular CLI tool for extracting AI-friendly text from **Git repositories**. Whether you're prepping data for ChatGPT, fine-tuning an LLM, or documenting codebases, Gittxt makes repository processing seamless.

---

## ✨ What's New in v1.5.0

- **🔄 Dynamic File-Type Filtering:**  
  Select exactly what you want extracted via `--file-types=code,docs,images,csv,media,all`

- **📦 Automatic ZIP Packaging:**  
  Automatically bundle non-text assets (images, CSVs, etc.) into ZIP archives.

- **🌳 Improved Tree + Summary Reports:**  
  Accurate directory tree and estimated token counts.

- **🔗 Smarter GitHub URL Parser:**  
  Supports branch & subdirectory parsing:  
  `https://github.com/user/repo/tree/dev/src/utils`

- **🚫 Cache-Free One-Time Scans:**  
  Fresh scan each time with automatic cleanup.

- **🌎 .env Config Support:**  
  Customize settings via environment variables.

- **🎨 Colored Logging (CLI):**  
  Easier to read logs with `--debug` or standard usage.

---

## 📥 Installation

### ⚡ Recommended (via Poetry)
```bash
pip install poetry
poetry install
```

### Or via PIP
```bash
pip install gittxt==1.5.0
```

---

## ⚙️ First-Time Setup
```bash
gittxt install
```
Interactive setup to configure:
- Output directory
- Logging preferences
- Default output format

---

## 🛠 Usage Examples

### ➤ Basic scan (local repo)
```bash
gittxt scan . --output-format txt
```

### ➤ Scan GitHub repo + branch + subdir
```bash
gittxt scan https://github.com/sandy-sp/gittxt/tree/main/src/gittxt/utils --output-format md
```

### ➤ Multi-repo + advanced options
```bash
gittxt scan ./repo1 https://github.com/user/repo2 --file-types code,docs --output-format txt,json --summary
```

### ➤ Fully automated (CI/CD ready)
```bash
gittxt scan ./repo --non-interactive --progress --file-types all
```

---

## 🎛 CLI Options

| Flag                        | Description                                              |
|-----------------------------|----------------------------------------------------------|
| `--file-types`              | Filter by `code`, `docs`, `images`, `csv`, `media`, `all`|
| `--output-format`           | txt, json, md, or multi-format e.g., `txt,json`          |
| `--include / --exclude`     | Fine-grained control via pattern matching                |
| `--size-limit`              | Exclude files larger than N bytes                        |
| `--summary`                 | Display token + size stats                               |
| `--non-interactive`         | Skips prompts (perfect for CI pipelines)                 |
| `--progress`                | Show progress bars while scanning                        |
| `--branch`                  | Specify branch for remote GitHub repositories           |

---

## 📂 Output Structure

```plaintext
<output_dir>/
├── text/      # TXT exports
├── json/      # JSON exports
├── md/        # Markdown exports
└── zips/      # ZIPs for non-code assets (images, csvs)
```

---

## 🧪 Running Tests
```bash
poetry run pytest tests/
```

---

## 📚 Configuration via `.env`

Example `.env` overrides:
```env
GITTXT_OUTPUT_DIR=./outputs
GITTXT_FILE_TYPES=all
GITTXT_OUTPUT_FORMAT=txt,json
```

---

## 💡 Contribute

1. **Fork + clone**
2. **New branch:** `feature/my-feature`
3. **Tests:** `poetry run pytest`
4. **PR it!**

---

## 🛣️ Roadmap
- FastAPI-powered UI
- AI-powered summaries (OpenAI / Ollama integration)
- More output formats (YAML, CSV exports)
- Async file scanning

---

## 📄 License
MIT License | Made by **[Sandeep Paidipati](https://github.com/sandy-sp)** 🚀

---

**Gittxt**: "Get Text of Your Repo for AI, LLMs & Docs!"

---
