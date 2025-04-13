# 🔌 `gittxt plugin` Command

The `plugin` command allows you to list, install, run, and uninstall Gittxt extensions like the API server or Streamlit UI.

---

## ✅ Syntax

```bash
gittxt plugin [subcommand] <plugin_name>
```

---

## 📋 Subcommands

| Command             | Description                                      |
|---------------------|--------------------------------------------------|
| `list`              | List all available plugins and their install status |
| `install <plugin>`  | Install a plugin from a local template           |
| `run <plugin>`      | Launch the plugin (installs dependencies automatically) |
| `uninstall <plugin>`| Remove the plugin folder                         |

---

## 🧰 Dependency Management

Each plugin manages its own dependencies via a `requirements.txt` file:

```text
plugins/gittxt-api/requirements.txt
plugins/gittxt-streamlit/requirements.txt
```

When you run a plugin using:

```bash
gittxt plugin run gittxt-api
```

The tool:
1. Checks for the plugin folder.
2. Installs dependencies from `requirements.txt`.
3. Launches the plugin using the specified run command.

This keeps the core CLI lightweight and free of plugin-specific dependencies like FastAPI or Streamlit.

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

- CLI warns if a plugin is already installed or missing.
- Installed plugins are sandboxed to the project directory.

---

## 🧪 Example

```bash
gittxt plugin list
gittxt plugin install gittxt-api
gittxt plugin run gittxt-api
```

---

Back: [Reverse](re.md)

