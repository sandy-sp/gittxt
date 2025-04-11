# Reverse Engineering from Gittxt Reports

The **`gittxt re`** command reconstructs the original source files from a Gittxt-generated `.txt`, `.md`, or `.json` report. This feature is especially useful for recovering repo content from a summarized archive or sharing code snapshots without the original repository.

---

## 📦 Supported Input Formats

- `.txt` – plain text Gittxt output
- `.md` – Markdown format
- `.json` – structured JSON format

All reports must follow the standard Gittxt output format as produced by the `gittxt scan` command.

---

## 🚀 Usage

```bash
gittxt re path/to/report.[txt|md|json]
```

This command will:
- Parse the provided Gittxt report
- Reconstruct all recognized source code files and directory structure
- Output a ZIP archive with the reconstructed repository contents

---

## 🧠 How It Works

1. **Report Parsing**  
   The tool detects the report format and extracts:
   - File paths
   - File contents (preserved in code blocks or text sections)

2. **Directory Reconstruction**  
   All directories are recreated using the original structure from the report.

3. **File Creation**  
   Each code/text file is restored to its proper location with full content.

4. **Packaging**  
   The reconstructed project is saved as a ZIP file, named after the top-level folder or repo name from the report.

---

## 📁 Output

After execution, a `.zip` file is created in the current directory:

```bash
Reconstructed archive: repo_name_reconstructed.zip
```

You can unzip this archive to view and work with the restored files.

---

## 📌 Example

```bash
gittxt re exports/my_project_summary.txt
```

Output:

```
Parsing report: my_project_summary.txt
Restoring 24 files...
Generated ZIP archive: my_project_reconstructed.zip
```

---

## 🛑 Limitations

- Binary or non-textual files (e.g. images, data files) cannot be reconstructed from `.txt` or `.md` formats.
- Only files included in the original Gittxt output are restored — excluded files (via filters or `.gittxtignore`) are not recoverable.
- Reports must be unmodified for best results. Manual edits may cause parsing issues.

---

## 🛠️ Pro Tips

- Use `.json` reports for the most reliable and structured reverse engineering.
- Include the `--lite` flag in `gittxt scan` only if minimal reconstruction is acceptable.

---

## 🔗 Related

- [Scanning Repositories](scan.md)
- [Gittxt Output Formats](formats.md)
- [CLI Reference](cli_reference.md)

```
