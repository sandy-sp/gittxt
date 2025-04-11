# 📡 API Reference Overview

The Gittxt API Plugin provides a RESTful interface for scanning GitHub repositories, uploading ZIP archives, and retrieving results programmatically.

This section documents the available endpoints, input models, and expected responses.

---

## 🚀 Getting Started

Launch the API server:
```bash
gittxt plugin run gittxt-api
```

Navigate to:
```text
http://localhost:8000/docs
```
To access the Swagger UI.

---

## 🔧 Available Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Check API status |
| `POST` | `/inspect` | Preview a repo without saving outputs |
| `POST` | `/scan` | Run full scan and save results |
| `POST` | `/upload` | Upload a ZIP and extract summaries |
| `GET` | `/download/{scan_id}` | Download results in `.txt`, `.json`, `.md`, or `.zip` |
| `GET` | `/summary/{scan_id}` | Fetch structured summary report |
| `DELETE` | `/cleanup/{scan_id}` | Remove scan outputs from disk |

---

## 🔑 Scan ID
Each scan creates a unique `scan_id` used to retrieve, download, or delete results.

---

## 📦 Output Format
Results are stored in the configured `OUTPUT_DIR` and returned via API responses or file downloads.

---

## 🔐 CORS & Security
- CORS is enabled for all origins by default.
- Add API key support in production environments.

---

Next: [Inspect Endpoint ➡](inspect-endpoint.md)

