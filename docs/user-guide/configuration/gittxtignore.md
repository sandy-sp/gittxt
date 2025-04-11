# 📄 Using .gittxtignore

The `.gittxtignore` file allows you to exclude specific files or directories from a Gittxt scan using gitignore-style syntax. It’s ideal for filtering out logs, binaries, or any content irrelevant to your dataset.

---

## 📌 Location
Place the `.gittxtignore` file in the **root of the repository or folder** you plan to scan.

---

## 🧠 How It Works
- Gittxt reads `.gittxtignore` patterns before scanning begins.
- These patterns take **precedence over CLI include/exclude patterns**.
- Filters apply only to the **current project** (not global).

---

## ✅ Supported Syntax
- File globs: `*.log`, `*.zip`
- Folder exclusions: `node_modules/`, `__pycache__/`
- Relative paths: `docs/temp.md`
- Comments: Lines starting with `#` are ignored

```text
# Ignore logs and temporary files
*.log
*.tmp

# Ignore build and test folders
build/
tests/

# Skip backup markdown files
README_backup.md
```

---

## ⚠️ Notes
- `.gittxtignore` is **not** the same as `.gitignore` (unless you use `--sync`).
- You can combine `.gittxtignore` with CLI options or config settings.

---

## 🔍 Debugging
Use debug mode to view active ignore patterns:
```bash
gittxt scan . --log-level debug
```

---

Next: [Interactive Config ➡](interactive-config.md)

