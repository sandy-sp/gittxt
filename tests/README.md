# 🧪 Gittxt Test Suite

This directory contains the full suite of automated tests for validating Gittxt’s CLI tool, API plugin, output formats, and reverse engineering logic.

---

## 📁 Folder Structure

```
tests/
├── cli/                   # CLI unit/integration tests
│   ├── generate_test_repo.py  # Creates CLI test repo with edge cases
│   └── test_*.py              # CLI feature tests (scanner, filters, zip, etc.)
│
├── api/                   # FastAPI plugin tests
│   ├── generate_test_repo.py  # Generates and zips API test repo
│   └── test_endpoints.py      # Endpoint coverage (health, scan, upload, etc.)
│
├── Makefile              # Test orchestration: CLI/API runs + cleanup
└── README.md             # This file
```

---

## ✅ Running Tests

### Full Test Suite (CLI + API)
```bash
make test
```

### Run CLI Tests Only
```bash
make cli-tests
```

### Run API Tests Only
```bash
make api-tests
```

### Run a Single Test
```bash
pytest tests/cli/test_scanner.py::test_scanner_with_exclude_pattern -v
```

---

## 🧪 Coverage Areas

- `cli/test_scanner.py` – include/exclude patterns, `.gittxtignore`, size limit
- `cli/test_output_formats.py` – rich formatting validation for `.txt`, `.json`, `.md`
- `cli/test_lite_mode.py` – lite mode exclusion of metadata
- `cli/test_zip_bundle.py` – ZIP bundling & manifest checks
- `cli/test_cli_run.py` – subprocess CLI testing
- `cli/test_reverse_engineer.py` – reconstruction from `.txt`, `.md`, `.json`
- `cli/test_subcat_utils.py` – subcategory inference for textual files
- `cli/test_repo_handler.py` – GitHub subdir cloning + local/invalid path handling
- `cli/test_cli_filters.py` – filter mutation via CLI
- `api/test_endpoints.py` – `/health`, `/scan`, `/upload`, `/summary`, `/cleanup`

---

## 🧼 Clean Up Test Artifacts

```bash
make clean
```

This deletes all auto-generated test folders and ZIPs:
```
tests/cli/test_repo/
tests/cli/cli_test_outputs/
tests/api/test_repo/
tests/api/test_repo.zip
```

---

## 🔄 Repo Generation

Tests dynamically generate structured repos using:
- `tests/cli/generate_test_repo.py`
- `tests/api/generate_test_repo.py`

These include:
- Valid + ignored text files
- Non-textual files
- Nested and hidden paths
- Minified, large, and CSV files
- `.gittxtignore` behavior

---

## 💡 Notes

- All tests are `pytest` based.
- Uses `async` fixtures and subprocess runners for realism.
- Each feature in Gittxt core has a corresponding test for stability.
- All tests are compatible with `--lite`, `--zip`, and tree-depth flags.

---

Happy testing 🚀
