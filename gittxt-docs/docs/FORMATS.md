# 📦 Output Formats in Gittxt

This document provides examples and detailed descriptions for each of the supported output formats in Gittxt.

---

## 📝 Text (.txt)

### Rich Mode
```
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

### Lite Mode
```
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

## 📊 JSON (.json)

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

## 📘 Markdown (.md)

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

[code here]


## 🎨 Non-Textual Assets
| Path | Type | Size | URL |
|------|------|------|-----|
| `logo.png` | Image | 12 kB | [Link](...) |
```

---

## 📆 ZIP Bundle (.zip)

Each ZIP archive includes:
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

### manifest.json
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

### summary.json
Mirrors the `summary` block from JSON formatter output.

---

For practical examples, see [`docs/USAGE_EXAMPLES.md`](USAGE_EXAMPLES.md).

