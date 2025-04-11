# 🛠 Interactive Configuration

Gittxt offers a built-in installer to guide you through setting up your configuration file. This creates a `gittxt-config.json` file and stores your preferences for future scans.

---

## 🚀 Run the Installer

```bash
gittxt config install
```

You’ll be prompted to define:
- 📁 Output directory
- 📄 Default output formats (e.g., `txt`, `json`, `md`)
- 🔊 Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- 📦 Auto-ZIP (enable or disable ZIP bundling)
- 🧩 File filters (textual/non-textual extensions)
- ❌ Excluded directories

---

## 📦 Where Config is Stored

After installation, your preferences are saved to:
```bash
src/gittxt/gittxt-config.json
```
You can edit this file manually or re-run the installer anytime.

---

## ✅ Sample CLI Usage After Install

Once configured, you can run:
```bash
gittxt scan .
```
Without passing extra flags — your defaults will be used automatically.

---

## 🧠 Why Use It?
- Simplifies CLI usage
- Creates a persistent setup across sessions
- Ideal for batch jobs or frequent usage

---

Next: [Filter Manager ➡](filter-manager.md)

