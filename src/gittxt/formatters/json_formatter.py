from pathlib import Path
import json
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.filetype_utils import classify_file

class JSONFormatter:
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
        output_file = self.output_dir / f"{self.repo_name}.json"
        data = {
            "repository_structure": self.tree_summary,
            "summary": generate_summary(text_files),
            "files": [],
        }
        for file in text_files:
            rel = Path(file).relative_to(self.repo_path)
            content = self.read_file_content(file)
            if content:
                data["files"].append({
                    "file": str(rel),
                    "content": content.strip(),
                    "file_type": classify_file(file)
                })
        with output_file.open("w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        return output_file
