# 🌍 Environment Variables

Gittxt supports environment variables to set default behaviors across all CLI invocations. These are useful for setting persistent preferences without editing the config file or passing flags every time.

---

## ✅ Common Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GITTXT_OUTPUT_DIR` | Default output directory | `~/gittxt_reports` |
| `GITTXT_OUTPUT_FORMAT` | Default formats | `txt,json,md` |
| `GITTXT_LITE_MODE` | Enable lite mode by default (`true`/`false`) | `true` |
| `GITTXT_AUTO_ZIP` | Automatically zip output (`true`/`false`) | `true` |
| `GITTXT_LOGGING_LEVEL` | Default logging level | `debug` |
| `GITTXT_SIZE_LIMIT` | Max file size in bytes | `1000000` |
| `GITTXT_LOG_FORMAT` | Logging style: `plain`, `json`, or `colored` | `json` |

---

## 🛠 How to Set

### Unix/macOS (bash/zsh)
```bash
export GITTXT_OUTPUT_DIR=~/gittxt_reports
export GITTXT_OUTPUT_FORMAT=txt,json
```

### Add to `.bashrc`, `.zshrc`, or `.env`
This ensures settings persist across terminal sessions.

### Windows (PowerShell)
```powershell
$env:GITTXT_OUTPUT_DIR = "C:\\Users\\you\\gittxt_reports"
```

---

## 📘 Notes
- CLI flags **always override** environment variables.
- If both environment variables and config file are set, environment values take precedence.

---

Next: [.gittxtignore ➡](gittxtignore.md)

