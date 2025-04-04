# 🧪 Usage Guide

Gittxt provides a flexible and modular CLI interface to scan repositories, configure filters, and generate structured outputs.

---

## 🔧 Core Command

```bash
gittxt scan [OPTIONS] [REPOS]...
```

Use this to scan a local folder or remote GitHub repo.

---

## ⚙️ Scan Options

| Option                                      | Description                                     |
|---------------------------------------------|-------------------------------------------------|
| `-o`, `--output-dir PATH`                   | Output directory path                           |
| `-f`, `--output-format TEXT`                | Comma-separated formats: `txt,json,md`          |
| `-i`, `--include-patterns TEXT`             | Glob patterns to include (textual files only)   |
| `-e`, `--exclude-patterns TEXT`             | Glob patterns to exclude                        |
| `--zip`                                     | Bundle outputs and assets into a `.zip` file    |
| `--lite`                                    | Generate lightweight summary outputs only       |
| `--sync`                                    | Respect `.gitignore` during scan                |
| `--size-limit INTEGER`                      | Skip files larger than this size (bytes)        |
| `--branch TEXT`                             | Git branch (for GitHub repos)                   |
| `--tree-depth INTEGER`                      | Max depth for directory tree rendering          |
| `--log-level [debug\|info\|warning\|error]` | Logging verbosity                               |

---

## 🚀 Common Examples

=== "📁 Local Scan"
    ```bash
    gittxt scan . --output-format txt,json
    ```

=== "🌐 GitHub Repo Scan"
    ```bash
    gittxt scan https://github.com/user/repo --output-format md --branch main
    ```

=== "🧼 Exclude Files"
    ```bash
    gittxt scan . --exclude-patterns "*.log" "node_modules/**"
    ```

=== "✅ Include Specific File Types"
    ```bash
    gittxt scan . --include-patterns "**/*.py" "**/*.md"
    ```

=== "📦 Bundle as ZIP"
    ```bash
    gittxt scan . --output-format txt,json --zip
    ```

=== "🌱 Shallow Tree Scan"
    ```bash
    gittxt scan . --tree-depth 2 --lite
    ```

---

## 🔁 Sync with `.gitignore`

Use `--sync` to automatically exclude files listed in your existing `.gitignore`:

```bash
gittxt scan . --sync
```

!!! note
    This does not replace `.gittxtignore`, but complements it.

---

## 📄 Using `.gittxtignore`

Create a `.gittxtignore` file in your repo root:

```
# .gittxtignore
*.zip
.env
images/
notebooks/
```

This overrides CLI `--exclude-patterns`.

---

## 🔧 Config Installer

Set up default preferences interactively:

```bash
gittxt config install
```

You’ll be prompted to set:
- Output directory and formats
- Logging level
- Default filters for text/non-text extensions
- Excluded directories

Settings are saved to `gittxt-config.json`.

---

## 🎛 Filter Manager

Manage filetype detection using:

```bash
gittxt config filters add textual_exts .ipynb
gittxt config filters remove non_textual_exts .log
```

Supported filter groups:
- `textual_exts`
- `non_textual_exts`
- `excluded_dirs`

You can also edit `gittxt-config.json` directly.

---

## 🔍 Logging Output

Control verbosity using `--log-level`:

```bash
gittxt scan . --log-level debug
```

Levels: `debug`, `info`, `warning`, `error`

Logs help trace:
- File classification
- Skipped reasons
- Scan summary

---

## 🧪 Testing CLI

Run a safe test scan:

```bash
gittxt scan . --output-format txt --lite --log-level info
```

Check:
- CLI output
- Logs
- Output files created

---

## 📘 See Also

- 🛠 [Getting Started](getting-started.md)
- ⚙️ [Configuration](configuration.md)
- 📘 [Output Formats](formats.md)
- 🧠 [API Reference](api-reference.md)

---
```

---

