# 🔌 Gittxt API Plugin

The **Gittxt API Plugin** enables a FastAPI-powered REST interface for scanning repositories, uploading ZIP files, and accessing scan summaries programmatically.

---

## 🚀 Launch the API

Start the server using the plugin CLI:
```bash
gittxt plugin run gittxt-api
```

Or directly via Uvicorn:
```bash
uvicorn plugins.gittxt_api.main:app --reload
```

Default URL: [http://localhost:8000](http://localhost:8000)

---

## 🛠 Features
- `/inspect`: Lightweight repo inspection (returns summary, no disk writes)
- `/scan`: Full scan and artifact generation (txt, json, md, zip)
- `/upload`: Accept ZIP uploads and return structured output
- `/download/{scan_id}`: Download any generated artifact
- `/summary/{scan_id}`: Return parsed scan summary
- `/cleanup/{scan_id}`: Remove scan artifacts from disk
- `/health`: Check API status

---

## 🔄 Input Model Example

```json
{
  "repo_path": "https://github.com/user/repo",
  "branch": "main",
  "include_patterns": ["**/*.py"],
  "exclude_dirs": ["tests"]
}
```

---

## 📦 Docker Support

To run in a containerized environment:
```bash
docker-compose -f plugins/gittxt_api/docker-compose.yml up
```

Or manually:
```bash
docker build -t gittxt-api -f plugins/gittxt_api/Dockerfile .
docker run -p 8000:8000 gittxt-api
```

---

## 🧪 Test the API

Use Swagger UI:
```text
http://localhost:8000/docs
```

Or send requests using Postman, Curl, or your preferred client.

---

## 🔐 Notes
- Each scan is assigned a unique `scan_id`
- Output is stored in the `OUTPUT_DIR`, configurable via environment

---

Back: [Plugins Overview](index.md) | Next: [Streamlit Plugin ➡](streamlit-plugin.md)

