# 🔌 Plugin System Overview

Gittxt supports a modular plugin system that allows you to extend its capabilities with optional tools and user interfaces.

This guide introduces the plugin system and how to interact with plugins using the CLI.

---

## 🧩 What Are Plugins?

Plugins are optional add-ons placed in the `plugins/` directory. They can include:
- 🧠 API servers (e.g., FastAPI backend)
- 🌐 Web UIs (e.g., Streamlit app)
- 🛠 Custom tools for export, post-processing, or automation

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

## ⚙️ Plugin Requirements
- Python dependencies are listed in `requirements.txt` or managed via Poetry
- Plugin `run` commands are defined in `cli_plugin.py`

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

