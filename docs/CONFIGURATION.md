# ⚙️ Gittxt Configuration Guide

This document explains how to configure Gittxt using the CLI, environment variables, and `.gittxtignore` files.

---

## 🧾 CLI Configuration

You can configure Gittxt behavior on a per-scan basis using CLI options:

```bash
gittxt scan . \
  --output-dir reports/ \
  --output-format txt,json,md \
  --lite \
  --zip \
  --size-limit 500000 \
  --exclude-patterns "*.zip" "*.png" \
  --include-patterns "**/*.py"
```

For complete options, run:

```bash
gittxt scan --help
```

---

## 🧑‍💻 Environment Variables

Set persistent defaults using environment variables:

| Variable               | Description                                    | Example          |
| ---------------------- | ---------------------------------------------- | ---------------- |
| `GITTXT_OUTPUT_DIR`    | Default output directory                       | `~/reports`      |
| `GITTXT_TREE_DEPTH`    | Default directory tree depth                   | `3`              |
| `GITTXT_AUTO_ZIP`      | Set to `true` to enable ZIP bundles by default | `true`           |
| `GITTXT_LITE_MODE`     | Set to `true` to enable lite mode by default   | `true`           |
| `GITTXT_SIZE_LIMIT`    | Default file size limit in bytes               | `1000000` (1 MB) |
| `GITTXT_LOGGING_LEVEL` | Logging verbosity (`debug`, `info`, `warning`) | `info`           |

Example:

```bash
export GITTXT_OUTPUT_DIR=~/reports
export GITTXT_LITE_MODE=true
export GITTXT_AUTO_ZIP=true
```

---

## 📄 `.gittxtignore` File

You can exclude files or directories using a `.gittxtignore` file placed in the root of your repository. It follows `.gitignore` syntax:

```text
# .gittxtignore
*.zip
images/
node_modules/
```

- Patterns listed here override defaults and CLI settings.
- Useful for project-specific exclusion management.

---

## 🔧 Filetype Filters

Manage filetype detection rules with CLI commands:

```bash
gittxt config filters add textual_exts .ipynb
gittxt config filters remove textual_exts .txt
```

Filter categories:

- `textual_exts`: Extensions classified as textual.
- `non_textual_exts`: Extensions classified as non-textual.
- `excluded_dirs`: Directories excluded from scans.

Manual editing via configuration (`config/gittxt-config.json`):

```json
{
  "filters": {
    "textual_exts": [".py", ".md", ".ipynb"],
    "non_textual_exts": [".zip", ".png"],
    "excluded_dirs": [".git", "node_modules"]
  }
}
```

---

For real-world examples, see [`docs/USAGE_EXAMPLES.md`](USAGE_EXAMPLES.md).

