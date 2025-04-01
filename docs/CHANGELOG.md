# 📦 Changelog

All notable changes to **Gittxt** will be documented in this file.

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

