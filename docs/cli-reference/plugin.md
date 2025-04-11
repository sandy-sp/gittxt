# 🔌 `gittxt plugin` Command

The `plugin` command allows you to list, install, run, and uninstall Gittxt extensions like the API server or Streamlit UI.

---

## ✅ Syntax
```bash
gittxt plugin [COMMAND] [PLUGIN_NAME]
```

---

## 🧩 Subcommands

### `list`
View available plugins and whether they are installed.
```bash
gittxt plugin list
```

---

### `install`
Install a plugin from local templates.
```bash
gittxt plugin install gittxt-api
```

---

### `uninstall`
Remove a plugin from your environment.
```bash
gittxt plugin uninstall gittxt-api
```

---

### `run`
Launch a plugin like the API or Streamlit interface.
```bash
gittxt plugin run gittxt-streamlit
```

---

## 📁 Plugin Paths
Plugins are located inside the project under:
```
plugins/
├── gittxt_api/
├── gittxt_streamlit/
```

Each plugin contains its own app files and configuration.

---

## ⚠️ Notes
- Plugin templates are expected in `plugin_templates/`
- CLI warns if a plugin is already installed or missing
- Installed plugins are sandboxed to the project directory

---

Back: [Reverse](re.md)

