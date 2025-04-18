# 📡 API Reference Overview

The Gittxt API Plugin provides a versioned RESTful interface for scanning GitHub repositories, uploading ZIP archives, and retrieving results programmatically. All routes are prefixed under `/v1`.

This section documents the available endpoints, input models, and expected responses.

---

## 🚀 Getting Started

Launch the API server:
```bash
gittxt plugin run gittxt-api
```

Then open:
```
http://localhost:8000/docs
```
This provides Swagger UI for all endpoints.

---

## 🔧 Available Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/v1/health` | Check API status |
| `POST` | `/v1/inspect` | Preview a repo (no outputs saved) |
| `POST` | `/v1/scan` | Full repo scan with output generation |
| `POST` | `/v1/upload` | Upload ZIP archive to scan |
| `GET` | `/v1/download/{scan_id}?format=txt|json|md|zip` | Download artifact |
| `GET` | `/v1/summary/{scan_id}` | View scan summary (JSON) |
| `DELETE` | `/v1/cleanup/{scan_id}` | Delete output artifacts by scan ID |

---

## 🔑 Scan ID
Every successful scan or upload returns a `scan_id`, which you can use to:
- Download results in various formats
- View summary data
- Cleanup temporary or saved files

---

## 📦 Output Format
Scan results are saved to a unique directory inside your configured `OUTPUT_DIR` and returned in:
- `.txt`, `.json`, `.md`
- `.zip` bundles (if `create_zip=true`)

---

## 🔐 CORS & Security Notes
- CORS is **enabled for all origins** (suitable for local or frontend integration)
- Consider implementing **API key authentication** in production
- All endpoints return structured `ApiResponse` objects with timestamp

---

## 📊 Response Schema Highlights

### `ApiResponse`
```json
{
  "status": "success",
  "message": "Scan completed successfully",
  "data": { ... },
  "timestamp": "2025-04-17T18:00:00Z"
}
```

### `ErrorResponse`
```json
{
  "status": "error",
  "error": "Validation Error",
  "detail": "...",
  "timestamp": "2025-04-17T18:00:00Z"
}
```

---

Next: [Inspect Endpoint ➡](inspect-endpoint.md)

