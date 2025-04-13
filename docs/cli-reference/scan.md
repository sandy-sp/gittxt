# 🛰️ `gittxt scan` Command

The `scan` command is the core entry point for extracting text and metadata from Git repositories or local folders.

---

## ✅ Syntax

```bash
gittxt scan [REPO_PATH or URL] [OPTIONS]
```

You can scan:
- A **local path**: `.` or `/path/to/repo`
- A **remote GitHub repo**: `https://github.com/user/repo`

---

## 📋 Key Options

| Flag | Description |
|------|-------------|
| `-o`, `--output-dir` | Where to write output files |
| `-f`, `--output-format` | Comma-separated: `txt`, `json`, `md` |
| `--zip` | Create a ZIP bundle of outputs |
| `--lite` | Minimal output (no metadata) |
| `--branch` | GitHub branch to scan (default: main) |
| `--tree-depth` | Limit tree rendering depth |
| `-i`, `--include-patterns` | Glob(s) to include |
| `-e`, `--exclude-patterns` | Glob(s) to exclude |
| `-x`, `--exclude-dir` | Directory names to exclude |
| `--size-limit` | Skip files larger than N bytes |
| `--sync` | Sync with `.gitignore` rules |
| `--log-level` | Logging level: `debug`, `info`, `error`, `warning` |
| `--docs` | Scan only documentation files (`*.md`) if `--include-patterns` not set |
| `--no-tree` | Exclude directory tree from output formats |

---

## 🔍 Examples

### Basic scan (local)
```bash
gittxt scan .
```

### Remote GitHub repo
```bash
gittxt scan https://github.com/user/repo
```

### Documentation-only scan
```bash
gittxt scan --docs https://github.com/user/repo
```

### Skip directory tree
```bash
gittxt scan --no-tree https://github.com/user/repo
```

### Advanced scan
```bash
gittxt scan . \
  -o out \
  -f txt,json \
  --zip --lite \
  -i "**/*.py" -e "tests/**" \
  --size-limit 100000
```

---

## 📁 Output Locations
Files are created in:
```
<output-dir>/txt/
<output-dir>/json/
<output-dir>/md/
<output-dir>/zip/
```
Use `--output-dir` to change this.

---

## 📊 Output Summary
Gittxt prints a terminal summary after scanning:
- Total files scanned
- Estimated tokens
- File type breakdown

To see skipped files, run with:
```bash
--log-level debug
```

---

Back: [CLI Overview](index.md) | Next: [Config ➡️](config.md)
