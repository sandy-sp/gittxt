# ⚡ Quickstart Guide

Welcome to the **Gittxt** quickstart! This guide walks you through your first scan using the `gittxt` CLI.

Gittxt lets you extract AI-ready textual datasets from local folders or GitHub repositories in seconds.

---

## 🚀 Minimal Scan (Local Folder)

If you're in a local Git project folder, run:

```bash
gittxt scan .
```

This will:
- Auto-detect textual files
- Generate `.txt` output in the default output directory

---

## 🌐 Scan a GitHub Repo

To scan a remote repository:

```bash
gittxt scan https://github.com/sandy-sp/gittxt
```

Use the `--branch` and `--subdir` flags to target specific content:

```bash
gittxt scan https://github.com/sandy-sp/gittxt --branch main --subdir src
```

---

## 🛠 Customize the Output

Use CLI options to control output format, zip bundling, lite mode, and filters:

```bash
gittxt scan . \
  --output-format txt,json \
  --zip \
  --lite \
  --include-patterns "**/*.py" "**/*.md" \
  --exclude-patterns "tests/*"
```

Common options:
- `--output-dir`: Custom location for exports
- `--output-format`: Any of `txt`, `json`, `md`
- `--zip`: Bundle everything in a zip
- `--lite`: Generate minimal reports (no metadata)
- `--size-limit`: Skip large files

---

## 🧾 Sample Output Structure

After scanning, output folders look like this:

```
<output-dir>/
├── txt/
├── json/
├── md/
├── zip/
│   ├── <repo-name>.zip
│   └── manifest.json, summary.json
```

---

## 📷 Demo

![Gittxt Demo](assets/gittxt-demo.gif)

---

## ✅ Success Checklist
- [x] CLI shows summary and breakdown
- [x] `.txt`, `.json`, or `.md` files appear in output dir
- [x] No errors or skipped files (check logs if needed)

---

## 🧠 Next Steps
- Learn advanced filters and exclusions in the [Scanning Guide](../user-guide/scanning.md)
- Configure project-wide defaults with [Configuration](../user-guide/configuration/index.md)

---

Back: [Installation](installation.md) | Forward: [User Guide ➡](../user-guide/scanning.md)

