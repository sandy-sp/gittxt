# 🌐 Gittxt Streamlit Plugin

The **Streamlit Plugin** provides a lightweight visual interface for Gittxt. It runs a local web app where users can input GitHub URLs, configure options, and download formatted outputs.

---

## 🚀 Launch the Web App

Start the plugin via CLI:
```bash
gittxt plugin run gittxt-streamlit
```

Or manually:
```bash
streamlit run plugins/gittxt_streamlit/app.py
```

Default URL: [http://localhost:8501](http://localhost:8501)

---

## 🎛 Features
- Enter any public GitHub repo URL
- Choose output format(s): `txt`, `json`, `md`
- Enable `lite` mode for summary-only reports
- Include ZIP bundle (optional)
- View summary report and file previews
- Download outputs from UI
- Restart button clears session and output dir

---

## 🧠 How It Works
- The app calls the `gittxt scan` CLI via subprocess
- All outputs are written to `plugin_output/`
- Streamlit reads generated `.json` for summary + preview

---

## 📁 Output Directory

```bash
plugin_output/
├── txt/
├── json/
├── md/
├── zip/
```

This folder is cleared when the Restart button is clicked.

---

## ⚠️ Notes
- Only one scan can run at a time
- Ensure output directory is empty before launching new scan
- Uses `subprocess.run` under the hood

---

## 💡 Tips
- Use in local, resource-constrained environments
- Streamlit state ensures that downloads don't trigger page reset

---

Back: [API Plugin](api-plugin.md)

