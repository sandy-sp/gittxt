# 🚀 Gittxt Usage Examples

This document provides practical examples of using Gittxt CLI for common tasks, demonstrating the latest available options and configurations.

---

## 📂 Basic Local Repository Scan

Scan your current directory and generate default outputs:

```bash
gittxt scan .
```

---

## 🚩 Specifying Output Formats and Directory

Generate reports in specific formats and place them in a custom output directory:

```bash
gittxt scan . --output-dir ./reports --output-format txt,json,md
```

---

## 🌟 Lite Mode

Generate minimal, lightweight outputs:

```bash
gittxt scan . --lite
```

---

## 📦 ZIP Bundle Creation

Include all outputs and assets in a ZIP archive:

```bash
gittxt scan . --zip
```

---

## 🚫 Exclude Files Using Patterns

Exclude specific files or types during scanning:

```bash
gittxt scan . --exclude-patterns "*.log" "*.tmp" "node_modules/*"
```

---

## ✅ Include Only Certain File Types

Limit scan to certain file types (e.g., only Python and Markdown files):

```bash
gittxt scan . --include-patterns "**/*.py" "**/*.md"
```

---

## 📄 `.gittxtignore` File Usage

Place a `.gittxtignore` file in your repository root with content:

```text
*.zip
images/
node_modules/
```

Enable syncing with `.gitignore`:

```bash
gittxt scan . --sync
```

---

## 📁 Scanning Remote Repositories

Scan a specific branch or subdirectory of a remote GitHub repository:

```bash
gittxt scan https://github.com/user/sample-repo --branch develop
```

---

## 🔧 Updating File Type Filters

Add or remove file types from detection filters:

```bash
gittxt filters add textual_exts .ipynb
gittxt filters remove textual_exts .log
```

---

For detailed configuration options, see [`docs/CONFIGURATION.md`](CONFIGURATION.md).

