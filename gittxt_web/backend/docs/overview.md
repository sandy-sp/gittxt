# gittxt API

`gittxt` converts source trees into token‑counted, LLM‑ready text artefacts.  
Primary use‑cases:

1. **Repository analysis** – estimate token cost before chunking.
2. **Automated red‑teaming** – extract only the text the model needs.
3. **Compliance** – immutable snapshot + summary JSON.

---

## Tiers

| Endpoint | Purpose | Persistence |
|----------|---------|-------------|
| `/v1/inspect` | *Quick peek* (no artefacts) | ❌ ephemeral |
| `/v1/scan`    | Full scan, returns a **scan_id** | ✅ artefacts saved |
| `/v1/summary/{scan_id}` | Get aggregate stats | ✅ |
| `/v1/download/{scan_id}` | Download TXT / JSON / MD / ZIP | ✅ |
