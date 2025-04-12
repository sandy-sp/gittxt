# 🧰 Installation Guide

Welcome to **Gittxt** — your tool for extracting clean, structured, AI-ready data from Git repositories.

This guide will help you install Gittxt in two ways:

- 📌 **Using pip (recommended)** for most users
- 🐍 **Using Poetry** for local development or contributions

---

## 📦 Install via PyPI (Recommended)

Gittxt is published on [PyPI](https://pypi.org/project/gittxt/).

```bash
pip install gittxt
```

After installation, you can run:

```bash
gittxt --help
```

---

## 🧪 Install for Local Development (Poetry)

This is the preferred method for contributors or developers making local changes.

### Step 1: Clone the Repo
```bash
git clone https://github.com/sandy-sp/gittxt.git
cd gittxt
```

### Step 2: Install Dependencies
```bash
poetry install
```

### Step 3: Run Gittxt
```bash
poetry run gittxt scan .
```

You can also install the CLI globally into your environment:
```bash
poetry install --editable .
```

---

## 🛠 Optional Setup: Interactive Configuration

To set up a default output directory, formats, filters, and logging options, run:

```bash
gittxt config install
```

This creates a `gittxt-config.json` file with your preferences.

---

## 🧪 Verify Installation

Run a basic scan to verify everything is working:
```bash
gittxt scan . --output-format txt --lite --log-level debug
```

You should see output directories created and summary info printed to your terminal.

---

## 🔧 Modular Installation Options (Poetry)

Gittxt is designed to be lightweight. You can install only what you need:

### 🧩 Core CLI Tool Only
This installs the base `gittxt` CLI without any plugin overhead:

```bash
poetry install
```

### 🔌 With Plugins (API & Streamlit)
If you plan to use the FastAPI backend or Streamlit dashboard:

```bash
poetry install --with plugins
```

### 🧪 With Dev Tools (for contributors)
Install development dependencies (tests, linting, formatting):

```bash
poetry install --with dev
```

You can also combine them:

```bash
poetry install --with plugins,dev
```

---

## 💬 Need Help?
If you face installation issues:
- Open an issue at [github.com/sandy-sp/gittxt/issues](https://github.com/sandy-sp/gittxt/issues)
- Or ask a question in [Discussions](https://github.com/sandy-sp/gittxt/discussions)

---

Next: [Quickstart ➡](quickstart.md)

