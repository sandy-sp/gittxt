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

    def read_file_content(self, file_path: Path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return None

    def generate_output(self, files, repo_path):
        tree_summary = generate_tree(Path(repo_path))

        # Split into two sets: text-convertible and non-text (assets)
        text_files = []
        asset_files = []

        for file in files:
            file_type = classify_file(file)
            if file_type in {"code", "docs", "csv", "text"}:
                text_files.append(file)
            elif file_type in {"image", "media"}:
                asset_files.append(file)

        # Handle TXT, JSON, MD outputs
        for fmt in self.output_formats:
            if fmt == "json":
                out = self._generate_json(text_files, tree_summary, repo_path)
            elif fmt == "md":
                out = self._generate_markdown(text_files, tree_summary, repo_path)
            else:
                out = self._generate_text(text_files, tree_summary, repo_path)

            logger.info(f"📄 {fmt.upper()} output ready at: {out}")

        # Zip non-code assets (images/csv/media)
        if asset_files:
            zip_path = self.zip_dir / f"{self.repo_name}_extras.zip"
            zip_files(asset_files, zip_path)
            logger.info(f"📦 Zipped non-text assets into: {zip_path}")

        return text_files

    def _generate_text(self, files, tree_summary, repo_path):
        output_file = self.text_dir / f"{self.repo_name}.txt"
        with output_file.open("w", encoding="utf-8") as out:
            out.write(f"📂 Repository Structure Overview:\n{tree_summary}\n\n")
            for file in files:
                rel = Path(file).relative_to(repo_path)
                content = self.read_file_content(file)
                if content:
                    out.write(f"=== FILE: {rel} ===\n")
                    out.write(content.strip())
                    out.write("\n\n" + "="*50 + "\n\n")
        return output_file

    def _generate_json(self, files, tree_summary, repo_path):
        output_file = self.json_dir / f"{self.repo_name}.json"
        data = {"repository_structure": tree_summary, "files": []}
        for file in files:
            rel = Path(file).relative_to(repo_path)
            content = self.read_file_content(file)
            if content:
                data["files"].append({
                    "file": str(rel),
                    "content": content.strip()
                })
        with output_file.open("w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        return output_file

    def _generate_markdown(self, files, tree_summary, repo_path):
        output_file = self.md_dir / f"{self.repo_name}.md"
        with output_file.open("w", encoding="utf-8") as out:
            out.write(f"# 📂 Repository Overview: `{self.repo_name}`\n\n")
            out.write(f"## 📜 Folder Structure\n```plaintext\n{tree_summary}\n```\n")
            out.write("## 📄 Extracted Files\n")
            for file in files:
                rel = Path(file).relative_to(repo_path)
                content = self.read_file_content(file)
                if content:
                    lang = self._detect_code_language(rel.suffix)
                    out.write(f"\n### `{rel}`\n```{lang}\n{content.strip()}\n```\n")
        return output_file

    def _detect_code_language(self, suffix: str) -> str:
        # Basic language hint for markdown fenced blocks
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".sh": "bash",
            ".json": "json",
            ".md": "markdown",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".txt": "plaintext"
        }
        return mapping.get(suffix.lower(), "plaintext")
    