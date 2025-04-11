# 🙌 Contributing to Gittxt

We’re thrilled that you’re considering contributing to **Gittxt**!

Whether you're fixing bugs, proposing features, improving docs, or writing tests — every contribution matters.

---

## 📜 Contribution Guidelines

### 1. 🔀 Fork the Repository

```bash
git clone https://github.com/YOUR-USERNAME/gittxt.git
cd gittxt
```

### 2. 🌱 Create a New Branch

Use feature or bugfix naming conventions:

```bash
git checkout -b feature/my-awesome-feature
```

### 3. 🎨 Follow Code Style

- Use **PEP8** conventions
- Format code with `black`:

```bash
poetry run black src/ tests/
```

---

## 🧪 Testing

Run the test suite using:

```bash
poetry run pytest
```

### ✅ All contributions **must**:
- Pass tests before submitting
- Include **new or updated tests** if applicable
- Keep coverage strong — we aim for **100% on formatters and core logic**

Test files are located in:

```
/tests/
```

---

## 🔁 Submit a Pull Request

1. Push your branch:

```bash
git push origin feature/my-awesome-feature
```

2. Open a PR via GitHub UI

- Clearly explain **what changed**
- Include screenshots/gif if UI output changed
- Reference related issues if applicable

---

## 🧩 Types of Contributions

- 🐛 Bug fixes
- ✨ New features
- 🧪 Test coverage
- 📝 Docs or Markdown improvements
- 💡 Ideas and feedback via [Discussions](https://github.com/sandy-sp/gittxt/discussions)

---

## 🛠 Local Setup with Poetry

```bash
poetry install
poetry run gittxt scan .
```

!!! tip "Use editable mode for fast testing"
    ```
    poetry install --editable .
    ```

---

## 💬 Need Help?

Open an issue or start a thread in [GitHub Discussions](https://github.com/sandy-sp/gittxt/discussions).

We’re always happy to help first-time contributors!

---

## 🛡 Code of Conduct

Please read our [Code of Conduct](code-of-conduct.md) before contributing.  
We value respectful and inclusive collaboration.

---

Thanks for helping make **Gittxt** better for the whole AI & dev community! ❤️

---
```

---
