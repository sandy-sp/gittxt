# 🔍 Inspect Endpoint

The `/v1/inspect` endpoint provides a lightweight preview of any GitHub or local repo.

Unlike `/scan`, this **does not write outputs to disk** or return ZIP bundles — it is intended for real-time frontend previews or quick backend checks.

---

## ✅ Endpoint
```http
POST /v1/inspect
```

---

## 🧾 Request Body
```json
{
  "repo_path": "https://github.com/user/repo",
  "branch": "main",
  "exclude_dirs": ["tests", "node_modules"],
  "include_patterns": ["**/*.py"],
  "exclude_patterns": ["*.log"]
}
```

### Fields
- `repo_path` (**required**): Local path or GitHub URL
- `branch` (optional): Defaults to `main`
- `exclude_dirs` (optional): Folders to skip
- `include_patterns` / `exclude_patterns`: Glob filters to include/exclude

---

## 📦 Response Example
Returns a summary and file listing without writing anything to disk:

```json
{
  "status": "success",
  "message": "Preview completed",
  "data": {
    "repository": {
      "name": "repo",
      "branch": "main",
      "tree_summary": "..."
    },
    "summary": {
      "total_files": 8,
      "estimated_tokens": 3000,
      "formatted": {
        "total_size": "28.1 kB",
        "estimated_tokens": "3k"
      }
    },
    "files": [
      {
        "path": "src/main.py",
        "subcategory": "code",
        "tokens_estimate": 1100,
        "url": "https://github.com/user/repo/blob/main/src/main.py"
      },
      ...
    ]
  },
  "timestamp": "2025-04-17T19:00:00Z"
}
```

---

## 🧠 Use Cases
- Live UI previews (before committing to a scan)
- Filter previews: let users choose patterns/directories dynamically
- Zero-write environments (e.g. sandboxed or ephemeral containers)

---

Back: [API Overview](index.md)

