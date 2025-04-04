# 📦 Changelog

All notable changes to **Gittxt** will be documented in this file.

---

## [1.7.0] - 2025-04-03

### 🧠 Config & Logging Enhancements
- Config file (`gittxt-config.json`) is now consistently stored in `src/gittxt/` instead of a nested `config/` folder.
- Log file (`gittxt.log`) is now created inside `src/gittxt/` and uses a rotating file handler for stability.
- CLI installer (`gittxt install`) updated to write to the correct config location using `ConfigManager`.
- Logging system now includes both stream and file output, and supports flexible format styles (`plain`, `json`, `colored`).

### ⚙️ CLI Restructure
- Combined `cli_install.py` and `cli_filters.py` into a new `cli_config.py` group with:
  - `gittxt config install` → interactive installer
  - `gittxt config filters` → subcommands for managing include/exclude patterns

### 📦 Formatter & ZIP Behavior
- Updated `text_formatter.py` and `markdown_formatter.py`:
  - Fixed missing `.strip()` on raw file content
  - Fixed malformed Markdown links for non-textual assets
- Validated that ZIP formatter bundles only current scan session outputs (no stale content), and follows expected behavior of full output capture per scan.

### 🧹 Repository & Scanner Improvements
- GitHub repositories now auto-detect their default branch (e.g., `main`, `master`, `dev`) if `--branch` is not specified.
- Scanner now logs a summary of accepted/skipped/non-textual files.
- Added warning when no textual files pass filters to prevent empty outputs.
- Cleaned up pattern matching explanations (glob-only, no regex) for better CLI usability.

---

## [1.6.0] - 2025-03-31

### ✨ Features
- Added `--lite` mode for minimal output across all formatters.
- Implemented `--zip` option to bundle outputs and non-textual assets into ZIP archives.
- Full asynchronous I/O support implemented for repository scanning and formatting.
- Added support for `.gittxtignore` to manage file/folder exclusions via gitignore-style patterns.
- Enhanced summary reports now display token counts, file-type breakdown, and detailed directory trees.

### 🛠 Improvements
- Modularized CLI into dedicated files: `cli_scan.py`, `cli_utils.py`, `cli_filters.py`, and `cli_install.py`.
- Improved directory tree generation with symlink support and configurable depth limits.
- Refactored formatters (`json_formatter.py`, `markdown_formatter.py`, `text_formatter.py`) for consistent behavior across rich and lite modes.
- ZIP formatter (`zip_formatter.py`) now includes `manifest.json` and `summary.json` in every bundle.
- Enhanced MIME-based file type heuristics in `filetype_utils.py` with fallback checks and improved accuracy.
- Optimized path handling and error management during file and asset bundling.

### 🧪 Tests
- Expanded test coverage for all formatters, notably ZIP bundling and lite-mode formatting.
- Enhanced scanner tests to cover `.gittxtignore` functionality, size limit handling, and glob pattern exclusions.
- Updated CLI tests to align with the newly modularized CLI structure.

### 🐛 Bug Fixes
- Fixed incorrect path resolution errors in multiple formatters causing test failures.
- Addressed crashes due to missing branch handling in CLI when scanning remote repositories.
- Resolved relative path calculation issues when creating ZIP bundles containing files outside the root directory.
- Improved skipped-file logging with clearer reasons and verbosity.
- Fixed CLI crash when invalid or inaccessible repositories were specified.

### 🧹 Cleanup
- Removed deprecated `--max-lines` CLI option.
- Eliminated redundant logging statements and obsolete utility functions.
- Streamlined configuration management logic for easier maintenance and readability.

---

## [1.5.9] - 2025-03-29

### ✨ Features
- Added `--lite` mode for minimal output format across all exporters
- Added `--zip` option to bundle outputs and non-textual assets
- Full async I/O support for scanning, file reads, and format generation
- `.gittxtignore` support to exclude files/folders using gitignore-style syntax
- Formatter outputs now include token count, file type breakdown, and tree summaries

### 🛠 Improvements
- Modularized CLI into `cli_scan.py`, `cli_utils.py`, `cli_filetypes.py`, `cli_install.py`
- Improved directory tree generation with better symlink handling and max-depth cap
- Formatter refactors for consistency, safer path resolution, and rich/lite modes
- Fallback logic for ZIP arcname generation when outputs fall outside root
- Markdown and JSON formatters now conditionally show empty asset sections
- Enhanced `filetype_utils.py` with better heuristics, MIME fallback, and async checks

### 🧪 Tests
- Added test coverage for all formatters including ZIP
- Improved scanner tests with `.gittxtignore`, size limits, pattern filters
- Rewrote invalid path, subdir scan, and repo handler tests for clarity

### 🐛 Bug Fixes
- Fixed `.resolve()` misuse in multiple formatters causing test failures
- Fixed `get_local_path()` crashing if `resolve()` wasn’t called
- Fixed CLI crashing when repo is invalid or missing branch
- Fixed relative path issues when bundling files from different output roots
- Fixed skipped reason logging with better verbosity and output flushing

### 🧹 Cleanup
- Removed deprecated `--max-lines` option
- Cleaned up redundant logging and unused utility functions

---

## [1.5.0] - 2024-12-20

Initial public release with:
- Repo scanning (local + remote)
- Textual classification
- TXT/JSON/Markdown output
- Token estimates
- Directory tree summary

