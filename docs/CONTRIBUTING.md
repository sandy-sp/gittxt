# 🙌 Contributing to Gittxt

Welcome! 🎉 We're excited that you're interested in contributing to **Gittxt**.

---

## 📜 Guidelines

### 1. **Fork the Repository**
Click the **Fork** button on the GitHub page and clone your fork locally:
```bash
git clone https://github.com/YOUR-USERNAME/gittxt.git
cd gittxt
```

### 2. **Create a New Branch**
Use a feature or bugfix branch:
```bash
git checkout -b feature/my-feature
```

### 3. **Code Style**
- Follow **PEP8** conventions.
- Use `black` for formatting:
  ```bash
  poetry run black src/ tests/
  ```

### 4. **Run Tests**
Make sure your changes pass tests:
```bash
poetry run pytest tests/
```

### 5. **Add/Update Tests**
- All new functionality should be covered by unit tests.
- Test files are located in the `/tests/` folder.

### 6. **Submit a Pull Request**
- Push your branch:
  ```bash
  git push origin feature/my-feature
  ```
- Open a PR on GitHub, explaining your changes.

---

## 🧩 Types of Contributions

- 🐛 Bug fixes
- ✨ New features (e.g., CLI options, output formats)
- 🧪 Unit tests
- 📝 Docs or README updates
- 💡 Ideas for roadmap items

---

## 🔍 Local Setup (with Poetry)
```bash
poetry install
poetry run pytest
```

---

## 🎉 Thank you!
Your contribution helps make Gittxt even better for the open-source community.

---

🛡 **Code of Conduct:**  
Please be kind and respectful to other contributors.

---
