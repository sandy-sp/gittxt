# 🙌 Contributing to Gittxt

Thank you for your interest in contributing to Gittxt!
This guide outlines how to get started with local development, contribute features or fixes, run tests, and follow coding standards.

---

## 🧭 Project Structure

```
src/gittxt/           # Core source code
├── cli/              # CLI subcommands
├── core/             # Scanner, repository handler, config, logger
├── formatters/       # Output builders for txt, json, md, zip
├── utils/            # Helper modules (file filters, summarizers)

plugins/              # Optional plugins (e.g., FastAPI, Streamlit)
tests/                # CLI and API test suite
```

---

## 🚀 Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/sandy-sp/gittxt.git
cd gittxt
```

### 2. Install Dependencies
```bash
poetry install
```

### 3. Use Editable Mode (Recommended for Dev)
```bash
poetry install --editable .
```

### 4. Run Gittxt
```bash
poetry run gittxt scan .
```

---

## ✅ Code Quality and Linting

Before pushing code or submitting a PR, please run:

```bash
make lint      # Fix issues with ruff
make format    # Format with black
make check     # Run ruff + black --check + poetry check
```

These help enforce:
- PEP8 code standards
- Auto-fixes for common issues
- Consistent formatting and static analysis

---

## 🧪 Running Tests

### Full Suite (CLI + API)
```bash
make test
```

### Only CLI Tests
```bash
make cli-tests
```

### Only API Tests
```bash
make api-tests
```

### Individual Test Example
```bash
pytest tests/cli/test_scanner.py::test_scanner_with_include_pattern -v
```

### Cleanup Test Outputs
```bash
make clean
```

---

## 🧠 What Tests Cover

- CLI flags: `--zip`, `--lite`, `--output-format`, include/exclude patterns
- `.gittxtignore` behavior and override priority
- ZIP bundle contents + manifest/summary integrity
- Markdown/JSON/TXT formatter correctness
- Subdirectory resolution and GitHub repo handling
- API routes: `/scan`, `/inspect`, `/upload`, `/summary`, `/cleanup`
- Reverse engineering from `.txt`, `.md`, `.json` reports
- Subcategory inference (e.g., code, config, data)

See full [Test Suite Docs](tests.md) for structure and coverage.

---

## 🔌 Working with Plugins

Plugins live in the `plugins/` directory and can be managed via:
```bash
poetry run gittxt plugin run gittxt-api
poetry run gittxt plugin run gittxt-streamlit
```

---

## 📦 Build Package Locally
```bash
make build
```
This builds the distribution using Poetry.

---

## 🧹 Clear Caches
```bash
make cache
```
Removes all `__pycache__` folders recursively.

---

## 🧑‍💻 Submitting a Pull Request

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-update
```

### 2. Follow Conventional Commits
Example:
```bash
git commit -m "feat(cli): add support for --tree-depth"
```

### 3. Push and Open PR
```bash
git push origin feature/your-update
```

- Clearly explain what changed
- Add screenshots or logs if needed
- Link related issues if applicable

---

## 🛡 Code of Conduct
Please follow our [Code of Conduct](code-of-conduct.md) in all interactions.

---

Thanks for helping improve **Gittxt** for the dev and AI community! ❤️

---

Next:
- [Code of Conduct ➡](code-of-conduct.md)
- [Gittxt Test Suite ➡](test.md)