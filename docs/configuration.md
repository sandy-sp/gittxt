# ⚙️ Configuration Guide

Gittxt supports multiple layers of configuration to customize how repositories are scanned, filtered, and formatted.

You can control behavior using:

- 🎛 CLI flags (per-command control)
- 🌍 Environment variables (persistent session-wide defaults)
- 📄 `.gittxtignore` files (project-specific exclusions)
- 🛠 Interactive config installer
- 🧩 Filetype filter manager

---

## 🎛 CLI Configuration (Per-Scan)

You can apply CLI options directly when running a scan:

```bash
gittxt scan . \
  --output-dir ./reports \
  --output-format txt,json \
  --zip \
  --lite \
  --size-limit 500000 \
  --exclude-patterns "*.zip" "images/*" \
  --include-patterns "**/*.py"
```

!!! tip
    CLI flags override both environment variables and config files.

---

## 🌍 Environment Variables

Set persistent defaults across sessions:

| Variable               | Description                                    | Example          |
|------------------------|------------------------------------------------|------------------|
| `GITTXT_OUTPUT_DIR`    | Default output directory                       | `~/reports`      |
| `GITTXT_TREE_DEPTH`    | Directory tree depth limit                     | `3`              |
| `GITTXT_AUTO_ZIP`      | Enable ZIP bundles by default (`true`/`false`) | `true`           |
| `GITTXT_LITE_MODE`     | Enable lite mode output                        | `true`           |
| `GITTXT_SIZE_LIMIT`    | Max file size in bytes                         | `1000000`        |
| `GITTXT_LOGGING_LEVEL` | Logging verbosity                              | `debug`          |

To set:
```bash
export GITTXT_OUTPUT_DIR=~/reports
export GITTXT_AUTO_ZIP=true
```

Add to `~/.bashrc`, `~/.zshrc`, or `.env` for persistence.

---

## 📄 `.gittxtignore` File

Place a `.gittxtignore` file in the root of your repository to exclude paths or patterns:

```text
*.zip
node_modules/
images/
README_backup.md
```

🧠 This supports:
- Glob patterns (`*.ext`)
- Folder exclusions
- Filename targeting

!!! info
    `.gittxtignore` takes precedence over CLI include/exclude patterns.

---

## 🛠 Interactive Config Installer

Run once to create a persistent config file:

```bash
gittxt config install
```

You’ll be prompted to define:

- 📁 Output path
- 📄 Default formats (`txt`, `json`, `md`)
- 🔊 Logging level
- 📦 ZIP bundling (`true/false`)
- 🎯 Filetype filters
- ❌ Excluded directories

The config is saved to:
```
src/gittxt/gittxt-config.json
```

---

## 🧩 Filter Manager

Manage file detection rules via subcommands:

```bash
# Add an extension as textual
gittxt config filters add textual_exts .ipynb

# Remove an extension from non-textual
gittxt config filters remove non_textual_exts .txt
```

Supported filter keys:
- `textual_exts`
- `non_textual_exts`
- `excluded_dirs`

You can also manually edit `gittxt-config.json`:

```json
{
  "filters": {
    "textual_exts": [".py", ".md", ".ipynb"],
    "non_textual_exts": [".zip", ".png"],
    "excluded_dirs": [".git", "node_modules"]
  }
}
```

---

## 🔁 `.gitignore` Sync (Optional)

Use `--sync` to sync exclusions with `.gitignore`:

```bash
gittxt scan . --sync
```

!!! warning
    This is opt-in and does not affect `.gittxtignore`.

---

## 🔍 View Active Configuration

Use `--log-level debug` during scan to see which settings and paths are in effect:

```bash
gittxt scan . --log-level debug
```

---

## 📘 Next Steps

- 🧪 [Usage Guide](usage.md)
- 📘 [Output Formats](formats.md)
- 🧠 [API Reference](api-reference.md)

---
```

---
