# ⚙️ `gittxt config` Command

The `config` command is used to manage Gittxt's configuration settings, including output preferences, logging behavior, and file filtering.

---

## ✅ Syntax

```bash
gittxt config [SUBCOMMAND]
```

---

## 🛠 Subcommands

### `install`
Launches an interactive configuration wizard:
```bash
gittxt config install
```
You’ll be prompted to:
- Choose output directory
- Select default output formats
- Set logging level
- Enable auto-ZIP
- Manage file filters

---

### `filters`
Manage file and folder filters used during scans.

```bash
gittxt config filters list
```
View current filters.

```bash
gittxt config filters add textual_exts .ipynb
```
Add new extensions to a filter category.

```bash
gittxt config filters remove non_textual_exts .csv
```
Remove extensions from filters.

```bash
gittxt config filters clear
```
Clear all filters.

Supported filter types:
- `textual_exts`
- `non_textual_exts`
- `excluded_dirs`

---

## 📝 Where Config is Stored
Configuration is saved to:
```
src/gittxt/gittxt-config.json
```
You can edit this file manually or use the CLI.

---

## 📘 Tips
- Filters affect which files are scanned or skipped
- Use `--log-level debug` with `gittxt scan` to see config details
- Settings persist across scans unless overridden via CLI flags

---

Back: [Scan](scan.md) | Next: [Clean ➡](clean.md)

