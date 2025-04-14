# 🔌 Plugin System Overview

Gittxt supports optional plugins to extend its functionality beyond the CLI.

Plugins currently include:
- 🧠 `gittxt-api`: FastAPI backend for web/app integrations
- 📊 `gittxt-streamlit`: Streamlit UI for interactive scans and downloads, now with full CLI parity and AI Summary support

---

## ⚙️ How Plugins Work

Each plugin:
- Resides under the `plugins/` directory
- Is launched using `gittxt plugin run <name>`
- Can be installed/uninstalled via CLI
- Manages its own dependencies via `requirements.txt`

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
gittxt plugin run gittxt-streamlit
```

---

## 🛠 Plugin Directory Structure

All plugins live under:
```
plugins/
├── gittxt_api/
├── gittxt_streamlit/
└── ...
```
Each plugin is self-contained with:
- `requirements.txt`
- Entrypoint script(s)
- Localized dependencies

---

## 🔧 How Dependency Installation Works

Each plugin has its own `requirements.txt`, such as:
```text
plugins/gittxt-api/requirements.txt
plugins/gittxt-streamlit/requirements.txt
```

When you run a plugin like:
```bash
gittxt plugin run gittxt-streamlit
```
Gittxt will:
1. Verify that the plugin is installed
2. Install missing dependencies automatically
3. Launch the plugin from the appropriate working directory

✅ This design keeps the **core CLI lightweight** and avoids unnecessary dependencies.

---

## 🔒 Safe Defaults
- All plugin paths are sandboxed inside the project repo
- No external fetching is done unless plugins are manually added
- Dependency installation is local to the plugin scope

---

Next:
- [API Plugin ➡](api-plugin.md)
- [Streamlit Plugin ➡](streamlit-plugin.md)

