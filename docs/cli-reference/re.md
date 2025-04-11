# 🔁 `gittxt re` Command

The `re` (reverse) command reconstructs the original repository structure from a Gittxt output report. This is useful when you only have `.txt`, `.md`, or `.json` exports and need the original source code files.

---

## ✅ Syntax
```bash
gittxt re REPORT_FILE [--output-dir PATH]
```

---

## 📄 Input
Supported input formats:
- `.json` (recommended)
- `.txt`
- `.md`

Each must follow Gittxt's output structure.

---

## 📦 Output
Creates a ZIP archive containing the reconstructed project.

### Example
```bash
gittxt re reports/project.json -o ./restored
```

Output:
```text
project_reconstructed_20250411.zip
```

---

## 🔍 What Gets Reconstructed
- Files listed in the report
- Full paths and folder structure
- Textual content only (no binary files)

---

## ⚠️ Limitations
- Lite mode reports have fewer details
- Markdown/text reports may lose metadata
- File content must be intact in the report

---

## ✅ Best Practices
- Prefer `.json` for best reconstruction
- Validate output using the tree view or unzip locally

---

Back: [Clean](clean.md) | Next: [Plugin ➡](plugin.md)

