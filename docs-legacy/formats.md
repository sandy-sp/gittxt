# 📦 Output Formats

Gittxt supports four structured output formats that capture directory trees, file metadata, and content summaries. You can choose one or more formats using the `--output-format` option:

```bash
gittxt scan . --output-format txt,json,md
```

---

## ✍️ `.txt` — Plain Text Format

The `.txt` format provides a readable summary with full content dumps of all textual files.

=== "Rich Mode (default)"
```text
=== Gittxt Report ===
Repo: sample-repo
Generated: 2025-03-31T12:34:56Z
Branch: main

=== Directory Tree ===
├── src
│   └── app.py
└── README.md

=== 📊 Summary Report ===
Total Files: 3
Total Size: 10.5 kB
Estimated Tokens: 3.2k

=== 📝 Extracted Textual Files ===
---> FILE: src/app.py | TYPE: Python | SIZE: 5.0 kB | TOKENS: 1.5k <---
[content here]
```

=== "Lite Mode"
```text
Repo: sample-repo
Branch: main

=== Directory Tree ===
├── script.py
└── data.md

=== Textual Files ===
---> File: script.py <---
[content here]
```

---

## 📊 `.json` — Machine-Readable Format

The `.json` output contains detailed metadata for integration with downstream tools or APIs.

```json
{
  "repository": {
    "name": "sample-repo",
    "url": "https://github.com/user/sample-repo",
    "branch": "main",
    "subdir": "src",
    "generated_at": "2025-03-31T12:34:56Z",
    "tree_summary": "├── src\n│   └── file.py"
  },
  "summary": {
    "total_files": 3,
    "total_size_bytes": 10240,
    "estimated_tokens": 3100,
    "formatted": {
      "total_size": "10.0 kB",
      "estimated_tokens": "3.1k",
      "tokens_by_type": {
        "Python": "1.5k"
      }
    },
    "file_type_breakdown": {
      "Python": 2,
      "Markdown": 1
    }
  },
  "files": [...],
  "assets": [...]
}
```

---

## 📘 `.md` — Markdown Format

This format is ideal for previewing the scan results in GitHub Pages, Jupyter notebooks, or Markdown editors.

```markdown
# 🧾 Gittxt Report for `sample-repo`

- **Generated**: 2025-03-31
- **Repository**: [GitHub URL]
- **Format**: markdown

## 📂 Directory Tree
├── src
│   └── app.py

## 📊 Summary Report
- **Total Files**: 3
- **Total Size**: 10.5 kB
- **Estimated Tokens**: 3.2k

## 📝 Extracted Textual Files
### `src/app.py` (Python)
- **Size**: 5.0 kB
- **Tokens (est.)**: 1.5k
- **URL**: [GitHub link]

[code block here]

## 🎨 Non-Textual Assets
| Path         | Type  | Size   | URL   |
|--------------|-------|--------|--------|
| `logo.png`   | Image | 12 kB  | [Link](...) |
```

---

## 📦 `.zip` — Archive Format

If you enable `--zip`, all generated outputs and assets are bundled in a reproducible archive:

```
repo-name-YYYYMMDD-HHMMSS.zip
├── outputs/
│   ├── sample-repo.txt
│   ├── sample-repo.json
│   └── sample-repo.md
├── assets/
│   └── image.png
├── summary.json
├── manifest.json
└── README.md
```

### `manifest.json`
A list of included files and assets:

```json
[
  {
    "type": "output",
    "name": "sample-repo.txt",
    "size_bytes": 10240,
    "size_human": "10.0 kB"
  },
  {
    "type": "asset",
    "path": "assets/image.png",
    "size_bytes": 12288,
    "size_human": "12.0 kB"
  }
]
```

### `summary.json`
A JSON mirror of the metadata block from `.json` output.

---

## 🔍 Choosing Formats

Use comma-separated values to generate multiple formats at once:

```bash
gittxt scan . --output-format txt,json,md
```

You can also combine formats with:
- `--lite` for minimal output
- `--zip` for bundling
- `--output-dir` for custom paths

---

## 📘 Related Docs

- 🧪 [Usage Guide](usage.md)
- ⚙️ [Configuration Options](configuration.md)
- 🧠 [API Reference](api-reference.md)

---
```

---
