from pathlib import Path
import json
from gittxt.logger import Logger
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.cleanup_utils import zip_files
from gittxt.utils.filetype_utils import classify_file
from gittxt.utils.summary_utils import generate_summary

logger = Logger.get_logger(__name__)


class OutputBuilder:
    """Handles output generation for scanned repositories."""

    BASE_OUTPUT_DIR = (Path(__file__).parent / "../gittxt-outputs").resolve()

    def __init__(self, repo_name, output_dir=None, output_format="txt"):
        self.repo_name = repo_name
        self.output_dir = (
            Path(output_dir).resolve() if output_dir else self.BASE_OUTPUT_DIR
        )
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

        text_files = []
        asset_files = []
        output_files = []

        for file in files:
            file_type = classify_file(file)
            if file_type in {"code", "docs", "csv", "text"}:
                text_files.append(file)
            elif file_type in {"image", "media"}:
                asset_files.append(file)

        for fmt in self.output_formats:
            if fmt == "json":
                out = self._generate_json(text_files, tree_summary, repo_path)
            elif fmt == "md":
                out = self._generate_markdown(text_files, tree_summary, repo_path)
            else:
                out = self._generate_text(text_files, tree_summary, repo_path)
            logger.info(f"📄 {fmt.upper()} output ready at: {out}")
            output_files.append(out)

        # Collect all output files + assets into ZIP
        if output_files or asset_files:
            zip_path = self.zip_dir / f"{self.repo_name}_bundle.zip"
            files_to_zip = output_files + asset_files
            zip_files(files_to_zip, zip_path)
            logger.info(f"📦 Zipped bundle created: {zip_path}")

        return text_files

    def _generate_text(self, files, tree_summary, repo_path):
        output_file = self.text_dir / f"{self.repo_name}.txt"
        with output_file.open("w", encoding="utf-8") as out:
            # Repo tree
            out.write(f"📂 Repository Structure Overview:\n{tree_summary}\n\n")

            # Summary FIRST
            summary = generate_summary(files)
            summary_str = "\n".join([f"{k}: {v}" for k, v in summary.items()])
            out.write("\n📊 Summary Report:\n")
            out.write(summary_str)
            out.write("\n\n")

            # Files section LAST
            for file in files:
                rel = Path(file).relative_to(repo_path)
                content = self.read_file_content(file)
                if content:
                    out.write(f"=== FILE: {rel} ===\n{content.strip()}\n\n{'='*50}\n\n")
        return output_file

    def _generate_json(self, files, tree_summary, repo_path):
        output_file = self.json_dir / f"{self.repo_name}.json"
        data = {
            "repository_structure": tree_summary,
            "summary": generate_summary(files),
            "files": [],
        }
        for file in files:
            rel = Path(file).relative_to(repo_path)
            content = self.read_file_content(file)
            if content:
                data["files"].append({"file": str(rel), "content": content.strip()})
        with output_file.open("w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4)
        return output_file

    def _generate_markdown(self, files, tree_summary, repo_path):
        output_file = self.md_dir / f"{self.repo_name}.md"
        with output_file.open("w", encoding="utf-8") as out:
            out.write(f"# 📂 Repository Overview: `{self.repo_name}`\n\n")
            out.write(f"## 📜 Folder Structure\n```\n{tree_summary}\n```\n")

            # Summary second
            summary = generate_summary(files)
            summary_md = "\n".join([f"- **{k}**: {v}" for k, v in summary.items()])
            out.write(f"\n## 📊 Summary Report\n\n{summary_md}\n")

            # Files section last
            out.write("\n## 📄 Extracted Files\n")
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
            ".txt": "plaintext",
        }
        return mapping.get(suffix.lower(), "plaintext")
