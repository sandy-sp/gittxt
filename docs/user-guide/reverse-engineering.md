# 🔁 Reverse Engineering

The `gittxt re` command allows you to reconstruct source code files from Gittxt-generated reports (`.txt`, `.md`, or `.json`). This is useful when you have a structured summary but not the original repository.

---

## 📂 Supported Formats

You can reverse engineer from any of the following report types:
- `.txt` — Plain text format
- `.md` — Markdown summary
- `.json` — Machine-readable export (most reliable)

Reports must follow the Gittxt output structure.

---

## 🚀 Usage

```bash
gittxt re path/to/report.[txt|md|json]
```

Optional:
```bash
--output-dir PATH  # Where to save the reconstructed ZIP
```

---

## 🧠 What Happens
1. Parses the selected report
2. Extracts file paths and contents
3. Reconstructs full directory structure
4. Saves all files into a ZIP archive

---

## ✅ Output Example

```bash
Parsing report: project_summary.json
Restoring 24 files...
Generated ZIP archive: project_reconstructed_20250411.zip
```

---

## 📁 Output Structure
```
project_reconstructed_<timestamp>.zip
├── src/
│   └── app.py
├── data/
│   └── dataset.csv
└── README.md
```

---

## ⚠️ Limitations
- Only files included in the original scan will be restored
- Binary/non-textual files are not recoverable from `.txt` or `.md`
- Edited reports may fail to parse
- If the report was created with --no-tree, the directory tree will be missing from reconstruction.
- If --lite was used, asset metadata and detailed formatting may be absent.

You may see CLI warnings like:
```bash
⚠️ Note: This report did not include a directory tree. Reconstructed structure may be limited.
⚠️ Note: No non-textual assets were included in this report.
```

---

## 💡 Tips
- Prefer `.json` for full fidelity
- Use `--lite` only if content summaries are sufficient

---

Back: [Output Formats](output-formats.md)

