# 🧪 Gittxt Test Suite Guide

This directory contains the full test suite for validating Gittxt’s scanning, formatting, and bundling functionality.

---

## 📁 Structure

```
tests/
├── test_repo/             # Auto-generated sample repo for scans
├── test_outputs/          # Formatter outputs
├── cli_test_outputs/      # CLI tests with different flags
├── test_zip_output/       # ZIP archive testing
├── generate_test_repo.py  # Creates controlled repo tree with edge cases
├── test_*.py              # Pytest test modules
```

---

## ✅ Running Tests

### Full Suite
```bash
make test
```
This will:
- Generate the test repository
- Run all tests with `pytest`
- Clean up all generated outputs

### Individual Test
```bash
pytest tests/test_scanner.py::test_scanner_with_exclude_pattern -v
```

---

## 🧱 What’s Covered
- CLI scanning with multiple flags (`--lite`, `--zip`, etc.)
- Scanner skips and includes based on config
- OutputBuilder across TXT, JSON, Markdown, ZIP
- Subdir resolution from remote repos
- Invalid path and error handling

---

## 🧹 Clean-up
Test outputs are auto-removed by `make test`.
To clean manually:
```bash
rm -rf tests/test_repo tests/test_outputs* tests/test_zip_output tests/cli_test_outputs
```

---

For more usage scenarios, see `docs/USAGE_EXAMPLES.md`

