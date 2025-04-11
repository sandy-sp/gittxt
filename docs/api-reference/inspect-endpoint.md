# 🔍 Inspect Endpoint

The `/inspect` endpoint provides a lightweight way to preview the contents of a GitHub repository without writing any output files to disk.

This is ideal for quick exploration and previews in frontend apps or dashboards.

---

## ✅ Endpoint
```http
POST /inspect
```

---

## 🧾 Request Body
```json
{
  "repo_path": "https://github.com/user/repo",
  "branch": "main",
  "exclude_dirs": ["tests", "node_modules"],
  "include_patterns": ["**/*.py", "**/*.md"],
  "exclude_patterns": ["*.log"]
}
```

### Fields:
- `repo_path` (required): Local path or GitHub URL
- `branch` (optional): Defaults to `main`
- `exclude_dirs` (optional): Folder names to ignore
- `include_patterns` / `exclude_patterns`: Glob filters

---

## 📦 Response Example
Returns the same structure as a JSON scan output, but **without saving files**:

```json
{
  "repository": {
    "name": "repo",
    "branch": "main",
    "tree_summary": "..."
  },
  "summary": {
    "total_files": 10,
    "estimated_tokens": 5000,
    "formatted": {
      "total_size": "42.3 kB",
      "estimated_tokens": "5k"
    }
  },
  "files": [ ... ]
}
```

---

## 🧠 Use Case
- Instant preview in UIs before full scan
- Run summaries with `lite` mode logic (no ZIP, no disk writes)
- Low-resource/ephemeral environments

---

Back: [API Overview](index.md)

