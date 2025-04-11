# 💻 CLI Reference Overview

The Gittxt CLI is organized into multiple subcommands, each focused on a specific task. This section provides an overview of all available commands.

---

## 📦 Core CLI Commands

| Command | Description |
|---------|-------------|
| `scan` | Scan a local or remote repository and generate outputs |
| `config` | Configure default settings, filters, and paths |
| `clean` | Remove previous scan outputs from the output directory |
| `re` | Reverse engineer a Gittxt report back into source files |
| `plugin` | Manage and run optional Gittxt plugins |

Each command has its own set of flags and options, documented in the following pages:

---

## 📘 Subcommand Docs
- [Scan ➡](scan.md): Run a repository scan
- [Config ➡](config.md): Install config, manage filters
- [Clean ➡](clean.md): Remove old outputs
- [Reverse ➡](re.md): Rebuild source code from a report
- [Plugin ➡](plugin.md): List, install, run optional plugins

---

## 🆘 Help Command
Use `--help` with any command to view inline help:

```bash
gittxt scan --help
gittxt config filters --help
```

---

Next: [Scan Command ➡](scan.md)

