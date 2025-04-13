# ⚙️ CLI Flags Reference

Gittxt provides powerful command-line options to control each scan. These flags override environment variables and config files for the duration of a single command.

---

## 🧾 General Flags

| Flag | Description |
|------|-------------|
| `-o`, `--output-dir` | Custom output directory for exports |
| `-f`, `--output-format` | Comma-separated formats: `txt`, `json`, `md` |
| `--zip` | Bundle all outputs into a ZIP archive |
| `--lite` | Generate minimal outputs (summary + raw content only) |

---

## 📁 Repository Options

| Flag | Description |
|------|-------------|
| `--branch` | Specify GitHub branch (for remote URLs) |
| `--subdir` | Scan a specific subdirectory of the repo |

---

## 🔍 Filtering Options

| Flag | Description |
|------|-------------|
| `-x`, `--exclude-dir` | Exclude directory paths (e.g., `node_modules`) |
| `-i`, `--include-patterns` | Include files matching glob patterns |
| `-e`, `--exclude-patterns` | Exclude files matching glob patterns |
| `--docs` | Scan only Markdown documentation files (*.md) if no include patterns given |
| `--size-limit` | Exclude files larger than specified size (in bytes) |

---

## 🧠 Behavior & Summary

| Flag | Description |
|------|-------------|
| `--branch` | GitHub branch to scan (defaults to `main`) |
| `--sync` | Use `.gitignore` if present (local only) |
| `--log-level` | Logging verbosity: `debug`, `info`, `error`, `warning` |
| `--no-tree` | Omit directory tree section from the output formats |
| `--tree-depth` | Restrict tree rendering to N levels |

---

## ✅ Example

```bash
gittxt scan . \
  -o ./reports \
  -f txt,json \
  --zip \
  --lite \
  -x .venv -x __pycache__ \
  -i "**/*.py" -i "**/*.md" \
  -e "*.log" \
  --size-limit 50000 \
  --log-level info
```

---

Next: [Environment Variables ➡](environment-variables.md)

