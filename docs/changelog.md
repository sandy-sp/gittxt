# 📜 Changelog

All notable changes to **Gittxt** are documented here.

We follow [Semantic Versioning](https://semver.org/) — breaking changes increase the major version, enhancements increase the minor, and bug fixes increase the patch.

---

## [1.7.5] - 2025-04-12

### 📝 Documentation
- Refreshed `README.md` to align with v1.7.x features and structure
- Linked new MkDocs documentation site in relevant sections
- Added dedicated sections for `clean`, `plugin`, and `reverse` commands
- Updated usage examples to reflect real CLI behavior and ZIP bundling logic

### 🚀 Features
- Introduced full plugin system section in README (API + Streamlit)
- Included reverse engineering usage and documentation highlights
- Clarified usage of `.gittxtignore`, `--lite`, and `--zip` modes in examples

### 🧹 Cleanup
- Removed outdated references to legacy usage docs (`docs/USAGE_EXAMPLES.md`)
- Refactored README badges, headings, and feature descriptions for consistency

## [1.7.4] - 2025-04-11

### 📚 Documentation
- Complete rewrite and reorganization of project documentation into MkDocs structure
- Added structured pages for CLI reference, plugin usage, API endpoints, and reverse engineering

### 🌐 Streamlit App
- Introduced `gittxt_streamlit` plugin
- Enables a visual UI for scanning GitHub repos
- Features file previews, summary rendering, and ZIP downloads

---

## [1.7.3] - 2025-04-11

### ✨ Features
- Introduced plugin management commands in the CLI:
  - `gittxt plugin list` to view available plugins.
  - `gittxt plugin install <plugin_name>` to install plugins.
  - `gittxt plugin uninstall <plugin_name>` to remove plugins.
  - `gittxt plugin run <plugin_name>` to execute installed plugins.
- Added `gittxt_api` plugin for running a FastAPI server:
  - Provides endpoints for scanning repositories, uploading ZIP files, and retrieving summaries.
  - Includes routes for cleanup, artifact downloads, and reverse engineering.

### 🛠 Improvements
- Enhanced `gittxt_api` plugin with:
  - CORS middleware for cross-origin requests.
  - Health check endpoint (`/health`) to verify API status.
  - Docker support with `Dockerfile` and `docker-compose.yml` for easy deployment.
- Improved CLI integration with plugins, allowing seamless management and execution.

### 🧪 Tests
- Added test coverage for plugin installation, uninstallation, and execution.
- Verified API endpoints for `gittxt_api` plugin, including scan, upload, and summary retrieval.

### 🐛 Bug Fixes
- Fixed issues with plugin path resolution in the CLI.
- Resolved minor logging inconsistencies in `gittxt_api` plugin.

---

## [1.7.2]

### Added
- New CLI command: `gittxt re` to reverse engineer source files from `.txt`, `.md`, or `.json` reports.
- Added `reverse_engineer.md` doc page and MkDocs nav entry.

---

## [1.7.0] - 2025-04-03

### 🧠 Config & Logging Enhancements
- Config file now stored in `src/gittxt/` (not `config/`)
- Log file uses a rotating handler and supports formats: `plain`, `json`, `colored`
- Installer updated to use `ConfigManager` correctly

### ⚙️ CLI Restructure
- Combined `cli_install.py` + `cli_filters.py` → `cli_config.py`
- New subcommands:
  - `gittxt config install`
  - `gittxt config filters`

### 📦 Formatter Fixes
- `.strip()` bug fixed in `text_formatter.py`
- Markdown links corrected for non-textual assets

### 🧹 Scanner Improvements
- Auto-detect default GitHub branch
- Logs summary: accepted/skipped/non-textual files
- Warning added when no textual files match filters

---

## [1.6.0] - 2025-03-31

### ✨ Features
- `--lite` mode for minimal output
- `--zip` option to bundle outputs/assets
- Full async I/O for scanning and formatting
- `.gittxtignore` support (gitignore-style exclusions)
- Token counts, file-type breakdowns, and tree summaries in report

### 🛠 Improvements
- CLI modularized into `cli_scan.py`, `cli_utils.py`, etc.
- Directory tree generator supports symlinks and depth config
- Formatter consistency across all modes
- ZIP bundles include `manifest.json`, `summary.json`
- MIME fallback detection improved in `filetype_utils.py`

### 🧪 Tests
- Expanded test coverage: formatters, `.gittxtignore`, glob filters
- CLI tests updated for modular CLI structure

### 🐛 Bug Fixes
- Path resolution bugs in formatters
- Missing branch errors handled during scan
- Fixed bundle paths escaping root directory
- Improved logging for skipped file reasons

### 🧹 Cleanup
- Removed deprecated `--max-lines`
- Cleaned logging and redundant utils

---

## [1.5.9] - 2025-03-29

### ✨ Features
- Introduced `--lite`, `--zip`
- Full async file reads
- Output includes summary metadata

### 🛠 Improvements
- Directory tree generator now more robust
- Markdown and JSON formatters handle empty asset sections
- Filetype heuristics + async MIME support

### 🐛 Bug Fixes
- `.resolve()` issues in formatters
- Crash handling for invalid repo/branch
- Relative path logic fixed for ZIP

---

## [1.5.0] - 2024-12-20

🎉 Initial public release!

- Scan local + remote repos
- Extract structured `.txt`, `.json`, `.md`
- Token estimates and directory tree
- Extension-based file filtering

---

