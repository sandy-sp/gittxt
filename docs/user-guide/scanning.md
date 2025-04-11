# 🔍 Scanning Repositories

The `gittxt scan` command is the core of the Gittxt CLI. It extracts structured, AI-ready outputs from local folders or GitHub repositories.

---

## 📦 Basic Usage

```bash
gittxt scan [REPO] [OPTIONS]
```

You can provide:
- A local path (e.g., `.`)
- A GitHub URL (e.g., `https://github.com/user/repo`)

---

## 🔧 Common Options

| Flag | Description |
|------|-------------|
| `-o`, `--output-dir` | Output location (default: `~/Gittxt`) |
| `-f`, `--output-format` | Formats: `txt`, `json`, `md` (comma-separated) |
| `--zip` | Bundle outputs into a `.zip` archive |
| `--lite` | Generate minimal reports (summary only) |
| `-x`, `--exclude-dir` | Exclude folder paths |
| `-i`, `--include-patterns` | Include only specific file globs |
| `-e`, `--exclude-patterns` | Exclude file globs |
| `--sync` | Sync with `.gitignore` rules |
| `--size-limit` | Skip files over N bytes |
| `--branch` | Branch name (GitHub repos only) |
| `--tree-depth` | Limit directory tree depth |
| `--log-level` | Logging level: `debug`, `info`, `warning`, `error` |

---

## 🌐 Scan Remote Repositories

```bash
gittxt scan https://github.com/sandy-sp/gittxt
```

Target a branch or subfolder:

```bash
gittxt scan https://github.com/user/repo --branch dev --subdir src
```

---

## 📁 Scan Local Directories

```bash
gittxt scan . --output-format txt,json
```

Exclude directories:
```bash
gittxt scan . -x node_modules -x tests
```

Include only Python and Markdown:
```bash
gittxt scan . -i "**/*.py" -i "**/*.md"
```

---

## ⚠️ Warnings and Tips

- `--branch` is ignored for local paths.
- If no textual files match the filters, you’ll see a warning.
- Use `--log-level debug` to see skipped files and reasons.

---

## ✅ Sample Command

```bash
gittxt scan https://github.com/user/repo \
  -f txt,json \
  --zip \
  --lite \
  -i "**/*.py" \
  -e "tests/**" \
  --log-level info
```

---

## 🧪 Next Steps
- Learn how to customize scan behavior with [Configuration](configuration/index.md)
- Explore available [Output Formats](output-formats.md)
- Reverse engineer previous scans with [Reverse Engineering](reverse-engineering.md)

---

Back: [Quickstart](../getting-started/quickstart.md)

