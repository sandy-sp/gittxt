# ⚙️ Configuration Overview

Gittxt supports multiple layers of configuration to customize scan behavior, output preferences, and file filtering.

This page introduces the different configuration mechanisms available. Each one can be used independently or in combination.

---

## 🔧 Configuration Layers

| Method | Scope | Use Case |
|--------|-------|----------|
| **CLI Flags** | Per-scan | One-off adjustments for format, filters, paths |
| **Environment Variables** | Session-wide | Persistent settings across scans |
| **Interactive Installer** | Persistent | First-time setup of default preferences |
| **`.gittxtignore` File** | Per-project | Exclude files/directories from scans |
| **Filter Manager** | Persistent | Override how Gittxt classifies file types |

---

## 📘 Configuration Topics

Gittxt's configuration is broken into the following guides:

- [CLI Flags](cli-flags.md): Command-line options like `--output-format`, `--lite`, etc.
- [Environment Variables](environment-variables.md): Customize behavior via `GITTXT_*` variables.
- [.gittxtignore](gittxtignore.md): Exclude files from a project using a gitignore-style file.
- [Interactive Config Installer](interactive-config.md): One-time setup for outputs, filters, and logging.
- [Filter Manager](filter-manager.md): Control classification of file types (textual vs. non-textual).

---

## 📁 Where Config is Stored

The persistent config is saved as:

```
src/gittxt/gittxt-config.json
```

This file is created by the installer and can be edited manually if needed.

---

## 🛠 View Active Settings

Use `--log-level debug` during scan to see active config values, matched filters, and output paths:

```bash
gittxt scan . --log-level debug
```

---

Next: [CLI Flags ➡](cli-flags.md)

