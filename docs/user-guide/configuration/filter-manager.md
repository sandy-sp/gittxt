# 🧩 Filter Manager

The filter manager lets you explicitly define which file extensions or directories are treated as textual, non-textual, or excluded from scans.

This provides fine-grained control beyond default heuristics.

---

## 🧠 Why Use It?
- Override file classifications
- Add new extensions (e.g., `.ipynb` as textual)
- Prevent false positives/negatives in filtering

---

## 🔧 Usage

View all current filters:
```bash
gittxt config filters list
```

Add a file extension:
```bash
gittxt config filters add textual_exts .ipynb
```

Remove a non-textual extension:
```bash
gittxt config filters remove non_textual_exts .csv
```

Clear all filters:
```bash
gittxt config filters clear
```

---

## 🎛 Supported Filter Keys

| Key | Description |
|-----|-------------|
| `textual_exts` | File extensions treated as textual |
| `non_textual_exts` | Extensions treated as non-textual |
| `excluded_dirs` | Folder names to ignore globally |

---

## 📝 Manual Edits
You can also modify `src/gittxt/gittxt-config.json` directly under the `filters` section:

```json
{
  "filters": {
    "textual_exts": [".py", ".md", ".ipynb"],
    "non_textual_exts": [".zip", ".pdf"],
    "excluded_dirs": [".git", "node_modules"]
  }
}
```

---

## 📘 Tips
- Conflicting extensions are automatically removed from the opposite group
- Use `--log-level debug` to verify how files are classified during scan

---

Next: [Output Formats ➡](../output-formats.md)

