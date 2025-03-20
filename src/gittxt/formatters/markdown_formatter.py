from pathlib import Path
from gittxt.utils.summary_utils import generate_summary

class MarkdownFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary

    def read_file_content(self, file_path: Path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return None

    def generate(self, text_files, asset_files):
        output_file = self.output_dir / f"{self.repo_name}.md"
        with output_file.open("w", encoding="utf-8") as out:
            out.write(f"# 📂 Repository Overview: `{self.repo_name}`\n\n")
            out.write(f"## 📜 Folder Structure\n```\n{self.tree_summary}\n```\n")

            summary = generate_summary(text_files + asset_files)
            summary_md = "\n".join([f"- **{k}**: {v}" for k, v in summary.items()])
            out.write(f"\n## 📊 Summary Report\n\n{summary_md}\n")

            out.write("\n## 📄 Extracted Files\n")
            for file in text_files:
                rel = Path(file).relative_to(self.repo_path)
                content = self.read_file_content(file)
                if content:
                    lang = self._detect_code_language(rel.suffix)
                    out.write(f"\n### `{rel}`\n```{lang}\n{content.strip()}\n```\n")

            if asset_files:
                out.write("\n## 📦 Asset Files\n")
                for asset in asset_files:
                    rel = Path(asset).relative_to(self.repo_path)
                    ext = rel.suffix.lower()
                    if ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]:
                        out.write(f"![{rel}]({rel})\n")
                    else:
                        out.write(f"- [{rel}]({rel})\n")
        return output_file

    def _detect_code_language(self, suffix: str) -> str:
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".sh": "bash",
            ".json": "json",
            ".md": "markdown",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".txt": "plaintext",
            ".ipynb": "json",
        }
        return mapping.get(suffix.lower(), "plaintext")
