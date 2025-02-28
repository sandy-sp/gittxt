# 🚀 Gittxt: Get Text of Your Repo for AI, LLMs & Docs!

**Gittxt** is a **lightweight CLI tool** that extracts text from **Git repositories** and formats it into **AI-friendly outputs** (`.txt`, `.json`, `.md`).  
Whether you’re using **ChatGPT, Grok, LLaMA**, or any LLM, Gittxt helps process repositories for insights, training, and documentation.

### ✨ Why Use Gittxt?
✅ **Extract Readable Text from Git Repos**  
✅ **Convert Code & Docs into AI-Friendly Formats**  
✅ **Generate JSON for LLM Training** (Ideal for AI Preprocessing)  
✅ **Create Markdown Files for Documentation**  
✅ **Summarize & Analyze GitHub Repositories**  

---

## 📌 Installation (From PyPI)
```bash
pip install gittxt
```
Verify installation:
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
  --output-dir TEXT
  --output-format [txt|json|md]
  --max-lines INTEGER
  --summary
  --debug
  --help  Show this message and exit.
```

---

## 📌 How to Use Gittxt

### **1️⃣ Extract Text from a Local Repository**
```bash
gittxt .
```
✅ Extracts all readable text from your repo into **gittxt-outputs/text/**.

---

### **2️⃣ Extract from a Remote GitHub Repo**
```bash
gittxt https://github.com/sandy-sp/sandy-sp
```
✅ Automatically clones the repo, scans it, and **extracts text**.

---

### **3️⃣ Use AI-Friendly Output Formats**
#### **🧠 JSON (Best for AI & LLM Training)**
```bash
gittxt . --output-format json --output repo_dump.json
```
**Why JSON?**
- **Perfect format for AI & LLMs** (GPT-4, Grok, LLaMA).
- **Prepares structured data for AI training**.
- **Can be used to fine-tune models with repository insights**.

#### **📜 TXT (For AI Chat & Analysis)**
```bash
gittxt . --output-format txt --output repo_dump.txt
```
**Why TXT?**
- **Extracts pure text**, making it easy for AI-powered chat analysis.
- **Good for summarization and AI-assisted code review**.

#### **📝 Markdown (Best for Documentation)**
```bash
gittxt . --output-format md --output repo_dump.md
```
**Why Markdown?**
- **Great for GitHub docs & project READMEs**.
- **LLMs like ChatGPT use Markdown for structured responses**.
- **Retains headings, code snippets, and structure**.

---

### **4️⃣ Get a Summary Report**
```bash
gittxt . --summary
```
Example Output:
```
📊 Summary Report:
 - Scanned 105 text files
 - Total Size: 3.2 MB
 - File Types: .py, .md, .txt
 - Saved in: gittxt-outputs/text/repo_dump.txt
```
✅ **Helps quickly analyze repositories for AI training**.

---

## 🆕 **What's New in v1.2.0?**
### ✅ **Bug Fixes & Enhancements**
- **Better file filtering (`--include`, `--exclude`)**.
- **Faster processing with improved caching**.
- **More accurate MIME-type detection**.

### 🚀 **New Features**
- **✅ Markdown Output (`--output-format md`)** → Generates AI-friendly structured docs.
- **📊 Summary Reports (`--summary`)** → Instantly view repo insights.
- **🔍 Debug Mode (`--debug`)** → See detailed logs of the extraction process.

---

## 📌 Contribute & Develop
### **1️⃣ Run Tests**
```bash
pytest tests/
```
### **2️⃣ Format Code**
```bash
black src/
```
### **3️⃣ Submit a PR**
1. **Fork the repo**
2. **Create a new branch (`feature/my-change`)**
3. **Push changes**
4. **Submit a PR!** 🚀

---

## 📜 License
Gittxt is licensed under **MIT**.

---

## **💡 Next Features Coming Soon!**
- [ ] **Interactive CLI for easy selection**  
- [ ] **Web UI for scanning repositories visually**  
- [ ] **Smarter AI-based file summarization**  

---

📌 **Made by [Sandeep Paidipati](https://github.com/sandy-sp)**
🚀 **Gittxt: Get Text of Your Repo for AI, LLMs & Docs!**

---