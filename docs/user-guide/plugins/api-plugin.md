# 🔌 Gittxt API Plugin

The Gittxt API Plugin exposes a RESTful interface for programmatic scanning and artifact retrieval. It's ideal for integrating Gittxt functionality into frontend dashboards, automation workflows, or other dev tools.

---

## 🚀 Quick Start

Run the API server:
```bash
gittxt plugin run gittxt-api
```

Once running, visit Swagger UI:
```
http://localhost:8000/docs
```

---

## 📌 Route Prefix
All endpoints are available under:
```
/v1/
```
Example:
```http
POST /v1/scan
```

---

## 🔧 Key Features
- Versioned REST API (`/v1/...`)
- Full scan options:
  - `docs_only`, `lite`, `create_zip`, `tree_depth`, `skip_tree`
  - Glob-based `include_patterns`, `exclude_patterns`, `exclude_dirs`
- Support for scanning uploaded ZIP files
- Summary JSON, downloadable artifacts, structured cleanup
- Built-in CORS support (for frontend integration)

---

## 📥 Upload & Scan
Use the `/v1/upload` endpoint to scan compressed `.zip` archives:

**Request**
```http
POST /v1/upload?lite=true
Content-Type: multipart/form-data
```
Payload: a `.zip` file with your repo.

**Response**
```json
{
  "status": "success",
  "message": "Upload & scan completed",
  "data": {
    "scan_id": "...",
    "repo_name": "...",
    "num_textual_files": 14,
    "num_non_textual_files": 3
  }
}
```

---

## 📡 Full Scan Example

```http
POST /v1/scan
Content-Type: application/json
```

**Payload:**
```json
{
  "repo_path": "https://github.com/user/repo",
  "branch": "main",
  "exclude_dirs": ["tests"],
  "include_patterns": ["**/*.py"],
  "exclude_patterns": ["*.log"],
  "lite": false,
  "create_zip": true,
  "tree_depth": 3,
  "docs_only": false,
  "sync_ignore": true,
  "skip_tree": false
}
```

**Response:**
Returns scan ID, summary, artifact paths, and file counts.

---

## 📦 Artifacts & Downloads
Use `/v1/download/{scan_id}?format=txt|json|md|zip` to fetch outputs.

Use `/v1/summary/{scan_id}` to get structured report metadata.

Use `/v1/cleanup/{scan_id}` to delete the generated folder and all artifacts.

---

## 🔐 Security Notes
- CORS is enabled for all domains by default.
- No authentication is applied — lock down via reverse proxy or key-based auth in production.

---

## 🛠 Developer Notes
This plugin is built with **FastAPI**, structured as:
```
src/plugins/gittxt_api/
├── api/v1/endpoints/...
├── core/services/...
├── cli_api.py
└── main.py
```

Dependencies are declared in `requirements.txt`. Running `gittxt plugin run gittxt-api` will install them automatically.


---

Back: [Plugins Overview](index.md) | Next: [Streamlit Plugin ➡](streamlit-plugin.md)

