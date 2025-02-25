# 📝 Gittxt: Extract Text from Git Repositories

**Gittxt** is a **lightweight CLI tool** that scans Git repositories (local or remote) and extracts text content into a **consolidated file** (`.txt`, `.json`).  
It is designed for **code summarization, AI preprocessing, offline reading, and documentation generation**.

🚀 **Features**  
- ✅ **Scan Local or Remote Repositories** (`git clone` support)  
- ✅ **Include & Exclude File Patterns** (`--include .py`, `--exclude node_modules`)  
- ✅ **Multi-threaded Scanning** (Optimized for large repositories)  
- ✅ **Supports JSON & TXT Output Formats** (`--format json`)  
- ✅ **Incremental Caching for Faster Scans** (Skips unchanged files)  
- ✅ **Force Full Rescan When Needed** (`--force-rescan`)  

---

## 📌 Installation (From PyPI)
Now available on PyPI! 🎉 Install it with:
```bash
pip install gittxt
```

✅ **Verify Installation**
```bash
gittxt --help
```
Expected Output:
```
Usage: gittxt [OPTIONS] SOURCE
Options:
  --include TEXT
  --exclude TEXT
  --size-limit INTEGER
  --branch TEXT
  --output TEXT
  --max-lines INTEGER
  --format [txt|json]
  --force-rescan
  --help  Show this message and exit.
```

---

## 📌 Usage Examples

### **1️⃣ Scan a Local Folder**
```bash
gittxt .
```
📌 **Result:** Outputs `gittxt_output.txt` containing extracted text.

---

### **2️⃣ Scan a Remote GitHub Repository**
```bash
gittxt https://github.com/torvalds/linux
```
📌 **This will:**
- Clone the **Linux Kernel repo** to a temporary directory.
- Extract **all readable text**.
- Save it in `gittxt_output.txt`.

---

### **3️⃣ Customize Output (JSON & TXT)**
✅ **Save as JSON (Structured Output)**
```bash
gittxt . --format json --output repo_dump.json
```

✅ **Save as TXT (Default)**
```bash
gittxt . --format txt --output repo_dump.txt
```

---

## 📌 🚀 New in `v1.0.0`
- **🎉 First official release on PyPI (`pip install gittxt`)**
- **🔄 Automatic caching for faster rescans**
- **📦 Multi-threaded scanning for large repos**
- **📝 Improved documentation & CLI stability**

---

## 📌 Development & Contribution
Want to contribute? Follow these steps:

### **1️⃣ Run Tests**
```bash
pytest tests/
```

### **2️⃣ Formatting & Linting**
```bash
black src/
```

### **3️⃣ Open a Pull Request**
1. **Fork the repo**
2. **Create a new branch** (`feature/my-change`)
3. **Push changes**
4. **Submit a PR!** 🚀

---

## 📌 License
This project is licensed under the **MIT License**.

---

## **🚀 Next Steps**
- **[ ] Add support for Markdown (`.md`) output.**
- **[ ] Implement a Web UI for visualization.**
- **[ ] Improve error handling for edge cases.**

---

📌 **Made by [Sandeep Paidipati](https://github.com/sandy-sp)**
```