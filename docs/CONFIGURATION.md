# ⚙️ Gittxt Configuration Guide

This document explains the available ways to configure Gittxt: via CLI, environment variables, and optional config files.

---

## 🧾 CLI Overrides (Most Common)

You can override behavior on a per-scan basis using CLI options:

```bash
gittxt scan . \
  --output-dir reports/ \
  --output-format txt,json,md \
  --lite \
  --size-limit 500000 \
  --exclude-patterns "*.zip" "*.png" \
  --include-patterns "**/*.py"
```

For full options, run:
```bash
gittxt scan --help
```

---

## 🧑‍💻 Environment Variables

You can set persistent defaults via environment variables:

| Variable | Description |
|----------|-------------|
| `GITTXT_OUTPUT_DIR` | Default directory to write outputs |
| `GITTXT_TREE_DEPTH` | Default directory tree max depth |
| `GITTXT_ZIP_BUNDLE` | Set to `1` to enable ZIP by default |
| `GITTXT_LITE_MODE`  | Set to `1` to enable lite output |

Example:
```bash
export GITTXT_OUTPUT_DIR=~/reports
export GITTXT_LITE_MODE=1
```

---

## 📄 JSON Config File (Coming Soon)

Support for a per-project `gittxt-config.json` is planned in future versions.
It will allow setting defaults like:

```json
{
  "output_dir": "docs/outputs",
  "exclude_patterns": ["*.zip", "*.bin"],
  "include_patterns": ["**/*.py"],
  "lite": true,
  "zip": true
}
```

Stay tuned for this feature in the roadmap.

---

## 🔧 Filetype Whitelist / Blacklist

You can override file type detection rules using:
```bash
gittxt filetypes add-textual .ipynb
```

This updates:
- `config/filetype_config.json`

You can also manually edit it:
```json
{
  "textual_exts": [".py", ".md", ".ipynb"],
  "non_textual_exts": [".zip", ".png"]
}
```

---

## 🧪 Testing Your Config

You can preview what’s picked up by using verbose + progress:
```bash
gittxt scan . --verbose --progress
```

Skipped files will print with reasons (e.g. filtered by size, non-textual).

---

For real-world examples, see `docs/USAGE_EXAMPLES.md`

