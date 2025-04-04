# 🚀 Getting Started

Welcome to **Gittxt** — your CLI companion for extracting clean, AI-ready datasets from Git repositories. This guide walks you through installing the tool, configuring your environment, and running your first scan.

---

## 📦 Installation

Gittxt supports both PyPI and Poetry-based installation.

=== "📌 Install from PyPI (recommended)"
    ```bash
    pip install gittxt
    ```

=== "🐍 Clone and Install with Poetry"
    ```bash
    git clone https://github.com/sandy-sp/gittxt.git
    cd gittxt
    poetry install
    poetry run gittxt install
    ```

The `gittxt install` step is optional and helps set default output directory, formats, and filtering rules.

---

## ⚙️ CLI Structure

Gittxt provides a modular CLI system:

```bash
gittxt [COMMAND] [OPTIONS]
```

Available commands:

- `scan` — Scan and extract from repos
- `config install` — Launch interactive config setup
- `config filters` — Manage include/exclude patterns

---

## 🔍 First Scan (Quickstart)

```bash
gittxt scan https://github.com/sandy-sp/gittxt --output-format txt,json --zip --lite
```

✅ This command will:
- Clone the remote GitHub repo
- Extract textual content
- Output `.txt` and `.json` summaries
- Package everything in a ZIP bundle

---

## 📁 Supported Sources

Gittxt can scan:
- Local repositories: `.` or any folder path
- Remote GitHub repos: with optional `--branch` and `--subdir`

Example:
```bash
gittxt scan . --output-format md,json
gittxt scan https://github.com/user/repo --branch main --subdir src
```

---

## 🧰 Optional Configuration

You can manage default behavior using:

=== "🧾 CLI Flags"
    ```bash
    gittxt scan . \
      --output-dir reports/ \
      --output-format txt,json \
      --lite \
      --zip \
      --exclude-patterns "*.png" "*.zip" \
      --include-patterns "**/*.py"
    ```

=== "🌍 Environment Variables"
    ```bash
    export GITTXT_OUTPUT_DIR=~/gittxt_reports
    export GITTXT_LITE_MODE=true
    export GITTXT_AUTO_ZIP=true
    ```

=== "📄 .gittxtignore File"
    Exclude paths using Git-like syntax:
    ```
    *.log
    secrets/
    node_modules/
    ```

Place this file in the **repo root**.

---

## 🖥 Directory Output Structure

After a scan, your output folder will look like:

```
<output-dir>/
├── text/
├── json/
├── md/
├── zips/
│   ├── <repo-name>.zip
│   └── manifest.json, summary.json
```

!!! note "Lite vs Rich Mode"
    Use `--lite` for minimal output. Omit it to include full metadata, summaries, and structured trees.

---

## 🧪 Verify Your Installation

Run this to test everything is working:

```bash
gittxt scan . --output-format txt --lite --log-level debug
```

Check:
- Output folders are created
- Files are summarized and saved
- No crashes or errors in logs

---

## 🛠 Next Steps

- 🔧 [Usage Guide](usage.md): CLI flags, filters, examples
- ⚙️ [Configuration Options](configuration.md): env vars, ignore files
- 📘 [Output Formats](formats.md): `.txt`, `.json`, `.md`, `.zip`

Need help? [Submit an Issue](https://github.com/sandy-sp/gittxt/issues)

---
```

---
