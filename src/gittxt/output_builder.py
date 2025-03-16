from pathlib import Path
import json
from gittxt.logger import Logger
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.cleanup_utils import zip_files
from gittxt.utils.filetype_utils import classify_file

logger = Logger.get_logger(__name__)

class OutputBuilder:
    """Handles output generation for scanned repositories."""

    BASE_OUTPUT_DIR = (Path(__file__).parent / "../gittxt-outputs").resolve()

    def __init__(self, repo_name, output_dir=None, output_format="txt"):
        self.repo_name = repo_name
        self.output_dir = Path(output_dir).resolve() if output_dir else self.BASE_OUTPUT_DIR
        self.text_dir = self.output_dir / "text"
        self.json_dir = self.output_dir / "json"
        self.md_dir = self.output_dir / "md"
        self.zip_dir = self.output_dir / "zips"

        self.output_formats = [fmt.strip().lower() for fmt in output_format.split(",")]

        for folder in [self.text_dir, self.json_dir, self.md_dir, self.zip_dir]:
            folder.mkdir(parents=True, exist_ok=True)

    def read_file_content(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return "[Error reading file]"

    def generate_output(self, files, repo_path):
        tree_summary = generate_tree(Path(repo_path))
        extras = []

        for fmt in self.output_formats:
            if fmt == "json":
                out = self._generate_json(files, tree_summary, repo_path)
            elif fmt == "md":
                out = self._generate_markdown(files, tree_summary, repo_path)
            else:
                out = self._generate_text(files, tree_summary, repo_path)
            logger.info(f"✅ Output generated: {out}")

        # Detect non-code files to ZIP
        extras = [Path(f) for f in files if classify_file(Path(f)) in {"image", "csv", "media"}]
        if extras:
            zip_path = self.zip_dir / f"{self.repo_name}_extras.zip"
            zip_files(extras, zip_path)
            logger.info(f"📦 Zipped non-code assets into: {zip_path}")

        return files

    def _generate_text(self, files, tree_summary, repo_path):
        output_file = self.text_dir / f"{self.repo_name}.txt"
        with output_file.open("w", encoding="utf-8") as out:
            out.write(f"📂 Repository Structure Overview:\n{tree_summary}\n\n")
            for file in files:
                rel = Path(file).relative_to(repo_path)
                out.write(f"=== {rel} ===\n")
                out.write(self.read_file_content(file) + "\n\n")
        return output_file

    def _generate_json(self, files, tree_summary, repo_path):
        output_file = self.json_dir / f"{self.repo_name}.json"
        data = {
            "repository_structure": tree_summary,
            "files": []
        }
        for file in files:
            rel = Path(file).relative_to(repo_path)
            data["files"].append({
                "file": str(rel),
                "content": self.read_file_content(file)
            })
        with output_file.open("w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        return output_file

    def _generate_markdown(self, files, tree_summary, repo_path):
        output_file = self.md_dir / f"{self.repo_name}.md"
        with output_file.open("w", encoding="utf-8") as out:
            out.write(f"# 📂 Repository Overview: {self.repo_name}\n\n")
            out.write(f"## 📜 Folder Structure\n```\n{tree_summary}\n```\n")
            out.write("## 📄 Extracted Files\n")
            for file in files:
                rel = Path(file).relative_to(repo_path)
                out.write(f"\n### `{rel}`\n```plaintext\n")
                out.write(self.read_file_content(file))
                out.write("\n```\n")
        return output_file
