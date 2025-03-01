# 🚀 Gittxt: Get Text of Your Repo for AI, LLMs & Docs!

**Gittxt** is a **lightweight CLI tool** that extracts text from **Git repositories** and formats it into AI-friendly outputs (`.txt`, `.json`, `.md`). Whether you’re using ChatGPT, Grok, Ollama or any LLM, Gittxt helps you process repositories for insights, training, and documentation.

---

## ✨ Why Use Gittxt?
- **Extract Readable Text:** Easily pull text from code, docs, and other repository files.
- **AI-Friendly Outputs:** Generate outputs in TXT, JSON, and Markdown for different use cases.
- **Efficient Processing:** Faster scanning with incremental caching.
- **Flexible Filtering:** Use advanced flags like `--docs-only` and `--auto-filter` to control what’s extracted.
- **Multi-Repository Support:** Scan one or more repositories in a single command.

---

## 🆕 Release v1.3.0

### New Features & Enhancements
- **Interactive Installation:**  
  Use the new `gittxt install` subcommand to set up your configuration (output directory, logging preferences, etc.) interactively.

- **Multi-Repository Scanning:**  
  Scan multiple repositories at once, whether they are local or remote.

- **Advanced Filtering Options:**  
  - `--docs-only`: Extract only documentation files (e.g., README, docs/ folder, etc.).
  - `--auto-filter`: Automatically skip common unwanted or binary files.

- **Multi-Format Output:**  
  Specify multiple output formats simultaneously (e.g., `--output-format txt,json,md`).

- **Enhanced Summary Reports:**  
  Outputs include summary statistics and an estimated token count for further AI processing.

- **Improved Logging & Caching:**  
  Faster, more accurate scanning with incremental caching and a rotating log file system.

---

## 📥 Installation

### Via PIP
```bash
pip install gittxt==1.3.0
```

### First-Time Setup (Interactive)
After installing, run:
```bash
gittxt install
```
This command will prompt you to configure:
- Your default output directory (automatically set based on your OS, e.g., `~/Gittxt/` on Linux/Mac)
- Logging level and file logging preferences

---

## 📌 How to Use Gittxt

### 1. Scanning Repositories
Use the `scan` subcommand to extract text and generate outputs.

#### Scan a Local Repository
```bash
gittxt scan .
```
Extracts all readable text into the default output directories.

#### Scan a Remote GitHub Repository
```bash
gittxt scan https://github.com/sandy-sp/sandy-sp
```
Automatically clones the repository, scans it, and extracts text.

#### Scan Multiple Repositories with Advanced Options
```bash
gittxt scan /path/to/repo1 https://github.com/user/repo2 --output-format txt,json --docs-only --auto-filter --summary
```

---

## 🔧 CLI Options

| Option                   | Description                                                               |
|--------------------------|---------------------------------------------------------------------------|
| `--include`              | Include only files matching these patterns.                              |
| `--exclude`              | Exclude files matching these patterns.                                   |
| `--size-limit`           | Exclude files larger than the specified size (in bytes).                 |
| `--branch`               | Specify a Git branch (for remote repositories).                          |
| `--output-dir`           | Override the default output directory.                                   |
| `--output-format`        | Comma-separated list of output formats (e.g., `txt,json,md`).               |
| `--max-lines`            | Limit the number of lines per file.                                      |
| `--summary`              | Display a summary report after scanning.                                 |
| `--debug`                | Enable debug mode for detailed logging.                                  |
| `--docs-only`            | Only extract documentation files (e.g., README, docs folder).              |
| `--auto-filter`          | Automatically skip common unwanted or binary files.                      |

---

## 📄 Output Formats

- **TXT:** Simple text extraction for AI chat and quick analysis.
- **JSON:** Structured output ideal for LLM training and data preprocessing.
- **Markdown (MD):** Neatly formatted documentation for GitHub or project READMEs.

When specifying multiple formats (e.g., `--output-format txt,json`), Gittxt generates separate files in their respective output directories.

---

## 🗂 Directory Structure

By default, outputs are stored in your configured output directory, which is organized as follows:
```
<output_dir>/
  ├── text/    # Plain text outputs (.txt)
  ├── json/    # JSON outputs (.json)
  ├── md/      # Markdown outputs (.md)
  └── cache/   # Caching for incremental scans
```

---

## ⚙️ Configuration

Gittxt uses a configuration file (`gittxt-config.json`) to store user preferences. You can update this configuration via the interactive install command:
```bash
gittxt install
```
Or edit the file manually. Key settings include:
- **Output Directory:** Auto-determined based on your OS (e.g., `~/Gittxt/`).
- **Logging Options:** Logging level and file logging preferences.
- **Filtering Options:** Include/exclude patterns, file size limits, etc.

---

## 📌 Contribute & Develop

1. **Run Tests:**
   ```bash
   pytest tests/
   ```
2. **Format Code:**
   ```bash
   black src/
   ```
3. **Submit a PR:**
   - Fork the repo.
   - Create a new branch (e.g., `feature/my-change`).
   - Push your changes.
   - Submit a PR.

For more details, see the [Contributing Guide](CONTRIBUTING.md).

---

## 💡 Future Roadmap

Our future plans include enhancements to the user interface and further AI-based features. We’re working on a lightweight web-based UI and additional improvements that streamline repository analysis and documentation extraction.

---

## 📜 License

Gittxt is licensed under the **MIT License**.

---

## **Made by [Sandeep Paidipati](https://github.com/sandy-sp)**
🚀 **Gittxt: Get Text of Your Repo for AI, LLMs & Docs!**

---