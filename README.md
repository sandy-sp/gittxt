# 📝 Gittxt: Extract Text from Git Repositories

**Gittxt** is a **lightweight CLI tool** that scans Git repositories (local or remote) and extracts text content into a **consolidated file** (`.txt` or `.json`).  
It is designed for **code summarization, AI preprocessing, offline reading, and documentation generation**.

🚀 **Features**  
- ✅ **Scan Local or Remote Repositories** (`git clone` support)  
- ✅ **Include & Exclude File Patterns** (`--include .py`, `--exclude node_modules`)  
- ✅ **Multi-threaded Scanning** (Optimized for large repositories)  
- ✅ **Supports JSON & TXT Output Formats** (`--format json`)  
- ✅ **Incremental Caching for Faster Scans** (Skips unchanged files)  
- ✅ **Force Full Rescan When Needed** (`--force-rescan`)  

---

## 📌 Installation

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/sandy-sp/gittxt.git
cd gittxt
```

### **2️⃣ Create & Activate Virtual Environment**
```bash
python3 -m venv venv
source venv/bin/activate  # For Linux/macOS
venv\Scripts\activate      # For Windows
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Install in Editable Mode (For Development)**
```bash
pip install -e src/
```

---

## 📌 Usage

### **1️⃣ Scan a Local Folder**
```bash
PYTHONPATH=src python src/gittxt/cli.py .
```
📌 **Result:** Outputs `gittxt_output.txt` containing extracted text.

---

### **2️⃣ Scan a Remote GitHub Repository**
```bash
PYTHONPATH=src python src/gittxt/cli.py https://github.com/torvalds/linux
```
📌 **This will:**
- Clone the **Linux Kernel repo** to a temporary directory.
- Extract **all readable text**.
- Save it in `gittxt_output.txt`.

---

### **3️⃣ Customize Output (JSON & TXT)**
✅ **Save as JSON (Structured Output)**
```bash
PYTHONPATH=src python src/gittxt/cli.py . --format json --output repo_dump.json
```

✅ **Save as TXT (Default)**
```bash
PYTHONPATH=src python src/gittxt/cli.py . --format txt --output repo_dump.txt
```

---

### **4️⃣ Include & Exclude Specific Files**
✅ **Scan Only Python Files**
```bash
PYTHONPATH=src python src/gittxt/cli.py . --include .py
```

✅ **Exclude `node_modules`, `.log` Files**
```bash
PYTHONPATH=src python src/gittxt/cli.py . --exclude node_modules --exclude .log
```

---

### **5️⃣ Improve Performance (Multi-threading)**
Gittxt **automatically optimizes scanning** based on repository size.

📌 **Want to manually set workers?** Use:
```bash
PYTHONPATH=src python src/gittxt/cli.py . --workers 8
```

---

### **6️⃣ Caching: Skip Unchanged Files for Faster Scans**
Gittxt **remembers previously scanned files** to **avoid redundant processing**.

✅ **First Scan (Full Processing)**
```bash
PYTHONPATH=src python src/gittxt/cli.py .
```
✅ **Second Scan (Uses Cache for Faster Results)**
```bash
PYTHONPATH=src python src/gittxt/cli.py .
```
🚀 **Faster! Skips unchanged files automatically!**

---

### **7️⃣ Force a Full Rescan (Ignore Cache)**
```bash
PYTHONPATH=src python src/gittxt/cli.py . --force-rescan
```
📌 **Deletes `.gittxt_cache.json` and scans everything from scratch.**

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

## 🚀 **Next Steps**
- **[ ] Improve error handling for edge cases.**
- **[ ] Add support for Markdown (`.md`) output.**
- **[ ] Implement a Web UI for visualization.**

---

**📌 Made by [Sandeep Paidipati](https://github.com/sandy-sp)**  


---