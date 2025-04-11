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
| `--log-level` | Log verbosity: `debug`, `info`, `warning`, `error` |

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
| `--sync` | Sync with `.gitignore` exclusions (optional) |
| `--size-limit` | Exclude files larger than specified size (in bytes) |

---

## 🌲 Tree and Summary Control

| Flag | Description |
|------|-------------|
| `--tree-depth` | Limit depth of rendered directory tree |

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

