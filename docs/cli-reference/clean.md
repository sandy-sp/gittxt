# 🧹 `gittxt clean` Command

The `clean` command removes previous output files from your configured output directory. It's helpful when resetting the environment between scans.

---

## ✅ Syntax
```bash
gittxt clean [OPTIONS]
```

---

## ⚙️ Options

| Flag | Description |
|------|-------------|
| `-o`, `--output-dir` | Target a specific directory (optional) |

If no `--output-dir` is provided, Gittxt will use the value from `gittxt-config.json`.

---

## 🧽 What It Cleans
Removes these subdirectories:
- `txt/`
- `json/`
- `md/`
- `zip/`
- `temp/`
- `reverse/`

Example:
```bash
gittxt clean -o ~/gittxt-output
```

---

## 🧠 Use Case
Run this before a fresh scan to:
- Prevent mixups with stale files
- Save disk space
- Reset directory structure

---

Back: [Config](config.md) | Next: [Reverse ➡](re.md)

