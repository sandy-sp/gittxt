# 📦 Output Formats

Gittxt supports multiple output formats to suit different use cases — from human-readable text to machine-parsable JSON. Choose one or more using the `--output-format` flag.

---

## ✍️ `.txt` — Plain Text

A readable report that includes:
- Directory tree
- Summary
- Full content of extracted files
- Non-textual asset list (if in rich mode)

Lite mode:
```bash
gittxt scan . --output-format txt --lite
```

---

## 📊 `.json` — Machine-Readable

Ideal for scripting, APIs, or analysis.
Includes:
- Structured metadata
- Token and size breakdowns
- File-level content

Rich mode JSON sample:
```json
{
  "repository": { ... },
  "summary": { ... },
  "files": [ ... ],
  "assets": [ ... ]
}
```

Lite mode includes just `path` and `content` for each file.

---

## 📘 `.md` — Markdown

Perfect for previewing results in Markdown editors or static sites.
Includes:
- Directory tree (in fenced code block)
- Text file previews
- Asset table (rich mode only)

Sample:
```markdown
## 📂 Directory Tree
```text
├── src
│   └── app.py
```
```

---

## 🗜 `.zip` — Bundled Archive

Use `--zip` to package all output formats and non-text assets:

```
<repo-name>-YYYYMMDD-HHMMSS.zip
├── outputs/
│   ├── repo.txt
│   ├── repo.json
│   └── repo.md
├── assets/
│   └── image.png
├── summary.json
├── manifest.json
├── README.md
```

### manifest.json
Lists files and sizes in the archive.

```json
[
  { "type": "output", "name": "repo.txt", "size_human": "5.4 kB" },
  { "type": "asset", "path": "assets/image.png", "size_human": "13.2 kB" }
]
```

---

## ✅ Choosing Formats

Generate multiple formats at once:
```bash
gittxt scan . --output-format txt,json,md --zip
```

Combine with:
- `--lite` for summary-only content
- `--tree-depth` to limit tree output

---

Next: [Reverse Engineering ➡](reverse-engineering.md)

