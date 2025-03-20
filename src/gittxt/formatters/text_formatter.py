from pathlib import Path
from gittxt.utils.summary_utils import generate_summary

class TextFormatter:
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

    def generate(self, text_files, _):
        output_file = self.output_dir / f"{self.repo_name}.txt"
        with output_file.open("w", encoding="utf-8") as out:
            out.write(f"📂 Repository Structure Overview:\n{self.tree_summary}\n\n")
            summary = generate_summary(text_files)
            out.write("\n📊 Summary Report:\n")
            out.write("\n".join([f"{k}: {v}" for k, v in summary.items()]))
            out.write("\n\n")
            for file in text_files:
                rel = Path(file).relative_to(self.repo_path)
                content = self.read_file_content(file)
                if content:
                    out.write(f"=== FILE: {rel} ===\n{content.strip()}\n\n{'='*50}\n\n")
        return output_file
