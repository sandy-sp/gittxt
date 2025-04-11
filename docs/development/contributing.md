# 🤝 Contributing to Gittxt

Thank you for your interest in contributing to Gittxt!
This guide outlines how to set up your environment, contribute code, and collaborate through pull requests.

---

## 🧱 Project Structure

```text
src/gittxt/
├── cli/        # CLI subcommands
├── core/       # Scanner, config, logger, builder
├── formatters/ # txt, json, md, zip output builders
├── utils/      # File + summary helpers
plugins/        # Optional extensions (e.g., API, Streamlit)
tests/          # Unit tests
```

---

## 🚀 Quickstart for Local Development

### 1. Clone the repository
```bash
git clone https://github.com/sandy-sp/gittxt.git
cd gittxt
```

### 2. Install dependencies (Poetry required)
```bash
poetry install
```

### 3. Run Gittxt
```bash
poetry run gittxt scan .
```

### 4. Use editable install for CLI testing
```bash
poetry install --editable .
```

---

## 🧪 Running Tests
Tests are located in the `tests/` folder.
```bash
poetry run pytest
```
To test a specific file:
```bash
poetry run pytest tests/test_scanner.py
```

---

## 🧩 Working with Plugins
- Plugins live in `plugins/`
- Run plugins via CLI:
```bash
poetry run gittxt plugin run gittxt-api
```
- Plugin templates go in `plugin_templates/`

---

## 🧼 Formatting & Linting
- Use [Black](https://black.readthedocs.io/) for formatting:
```bash
poetry run black src/ tests/
```
- Ensure commits pass lint and tests

---

## 🌍 Submitting a Pull Request
1. Fork the repository
2. Create a feature branch
```bash
git checkout -b feature/my-contribution
```
3. Commit with a clear message
```bash
git commit -m "feat(cli): add reverse scan from report"
```
4. Push to your fork and open a PR

---

## 🛡 Code of Conduct
All contributors are expected to follow our [Code of Conduct](code-of-conduct.md).

---

Happy building 🚀

