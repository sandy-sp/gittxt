# 🧪 Gittxt Test Suite

This page documents the full test suite for Gittxt, including how tests are structured, executed, and maintained across CLI and API components.

---

## 📁 Test Directory Structure

```
tests/
├── cli/                   # CLI unit & integration tests
│   ├── generate_test_repo.py  # Creates edge-case test repos
│   └── test_*.py              # Scanner, filters, formats, ZIP, reverse tests
│
├── api/                   # FastAPI plugin test coverage
│   ├── generate_test_repo.py
│   └── test_endpoints.py
│
├── Makefile              # Unified test runner and cleaner
└── README.md             # Dev guide for tests
```

---

## ✅ How to Run Tests

### Run All Tests
```bash
make test
```

### Run Only CLI Tests
```bash
make cli-tests
```

### Run Only API Tests
```bash
make api-tests
```

### Run a Specific Test
```bash
pytest tests/cli/test_scanner.py::test_scanner_with_exclude_pattern -v
```

---

## 🧪 What We Test

### Core CLI
- `test_scanner.py`: filters, `.gittxtignore`, size limits, skipped reasons
- `test_output_formats.py`: `.txt`, `.json`, `.md` rich output validation
- `test_lite_mode.py`: ensures lite mode strips metadata
- `test_zip_bundle.py`: verifies contents of generated ZIP archives
- `test_cli_run.py`: end-to-end CLI subprocess testing
- `test_cli_filters.py`: interactive CLI filter updates

### Reverse Engineering
- `test_reverse_engineer.py`: reconstructs repos from `.txt`, `.md`, `.json`

### API Plugin
- `test_endpoints.py`: tests `/health`, `/scan`, `/summary`, `/download`, `/upload`, `/cleanup`

### Utilities
- `test_repo_handler.py`: GitHub repo resolution, subdir support
- `test_formatter_sorting.py`: README prioritization in file sorting
- `test_subcat_utils.py`: sub-category detection (`docs`, `config`, `code`)

---

## 🔄 Repo Generation for Tests

Two scripts generate test repositories with realistic edge cases:

- `tests/cli/generate_test_repo.py`
- `tests/api/generate_test_repo.py`

These include:
- Minified JS files
- Large files over 5MB
- Binary/non-textual content
- `.gittxtignore`-excluded paths
- Hidden and extensionless files
- Deeply nested folders

---

## 🧼 Cleaning Up

To clean all test-generated content:

```bash
make clean
```

This will remove:
- `tests/cli/test_repo/`
- `tests/cli/cli_test_outputs/`
- `tests/api/test_repo/`
- `tests/api/test_repo.zip`

---

## 💡 Best Practices

- Run `make test` before every PR submission.
- Use `--log-level debug` with `gittxt scan` to trace test outputs.
- Keep `.gittxtignore` scenarios up to date in `generate_test_repo.py`.
- Reverse engineer tests help validate report integrity for `.txt`, `.md`, `.json`.

---

Need help writing new tests? Open an issue or ping us in [GitHub Discussions](https://github.com/sandy-sp/gittxt/discussions).

Happy testing 🚀

---

Back: [Contributing](contributing.md)