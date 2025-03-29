# 📘 Gittxt Usage Examples

This guide provides practical examples of how to use the `gittxt` CLI for scanning repositories, applying filters, and generating outputs in different formats.

---

## 🛠 Basic Scan

Scan a local or remote repository and output results in default formats (TXT + JSON):

```bash
gittxt scan https://github.com/some-user/some-repo
```

This creates:
- `some-repo.txt`
- `some-repo.json`

in the configured output directory.

---

## 📂 Scanning a Subdirectory

Target a specific subfolder within a GitHub repo:

```bash
gittxt scan https://github.com/org/repo --branch main --output-dir out --lite --zip
```

Add a subdir:

```bash
gittxt scan https://github.com/org/repo --subdir src/lib --zip
```

---

## 🧹 Exclude Directories and Files

Skip node_modules, virtualenvs, or specific patterns:

```bash
gittxt scan . -x node_modules -x venv -e "*.zip" -e "*.png"
```

Also supports `.gittxtignore`:

```text
# .gittxtignore
*.zip
images/
```

---

## ✅ Include Only Specific File Patterns

Restrict to files matching given globs:

```bash
gittxt scan . -i "**/*.py" -i "*.md"
```

Only `.py` and `.md` files will be considered textual.

---

## 🚫 Size Limit

Ignore large files:

```bash
gittxt scan . --size-limit 1000000  # 1MB
```

---

## 📦 Create a ZIP Bundle

Package all outputs + assets + manifest:

```bash
gittxt scan . --zip
```

This generates:
- `repo-name-YYYYMMDD-HHMMSS.zip`
  - `outputs/*.txt`, `*.json`, `*.md`
  - `assets/` folder for images, binaries
  - `summary.json`, `manifest.json`, `README.md`

---

## ⚡️ Lite Mode Output

For minimal reports without full content:

```bash
gittxt scan . --lite
```

---

## 📁 Output Directory

Customize where outputs are saved:

```bash
gittxt scan . --output-dir ./my-reports
```

---

## 🧪 Running on Test Repo

```bash
make test
```

This runs:
- `generate_test_repo.py`
- full pytest suite on test cases

---

For advanced configuration, see `docs/CONFIGURATION.md`

