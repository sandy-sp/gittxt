# 🔌 Plugin System Overview

Gittxt supports optional plugins to extend its functionality beyond the CLI.

Plugins currently include:
- 🧠 `gittxt-api`: FastAPI backend for web/app integrations
- 📊 `gittxt-streamlit`: Streamlit UI for interactive scans and downloads

---

## ⚙️ How Plugins Work

Each plugin:
- Resides under the `plugins/` directory
- Is launched using `gittxt plugin run <name>`
- Can be installed/uninstalled via CLI

---

## 🚀 Plugin Lifecycle

You can manage plugins using:
```bash
gittxt plugin [COMMAND]
```

### Available Commands:
| Command | Description |
|---------|-------------|
| `list` | Show available and installed plugins |
| `install <name>` | Install a plugin (from internal template) |
| `uninstall <name>` | Remove a plugin from your system |
| `run <name>` | Launch a plugin (e.g., API server, Streamlit UI) |

### 🧪 Example Commands
```bash
gittxt plugin list
gittxt plugin install gittxt-api
gittxt plugin run gittxt-api
```

---

## 🧰 Plugin Directory

All plugins live under:
```
plugins/
├── gittxt_api/
├── gittxt_streamlit/
└── ...
```
Each plugin is self-contained with its own dependencies and entry points.

---

## 🧰 Plugin Requirements

Each plugin has its own `requirements.txt`. For example:

```text
plugins/gittxt-api/requirements.txt
plugins/gittxt-streamlit/requirements.txt
```

When you run a plugin via:
```bash
gittxt plugin run gittxt-streamlit
```
Gittxt will:
1. Check if the plugin is installed
2. Automatically install any required dependencies from `requirements.txt`
3. Launch the plugin in the correct working directory

✅ This keeps the **core CLI lightweight** and avoids bundling unnecessary dependencies.

---

## 🔗 Examples

### Launch Streamlit App
```bash
gittxt plugin run gittxt-streamlit
```

### Launch FastAPI Server
```bash
gittxt plugin run gittxt-api
```

---

## 🔒 Safe Defaults
- All plugin paths are sandboxed inside the project repo
- No plugins are fetched from external sources unless added manually

---

Next:
- [API Plugin ➡](api-plugin.md)
- [Streamlit Plugin ➡](streamlit-plugin.md)

