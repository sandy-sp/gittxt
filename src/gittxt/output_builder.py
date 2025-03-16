from pathlib import Path
import json
from gittxt.logger import Logger
from gittxt.utils.tree_utils import generate_tree

logger = Logger.get_logger(__name__)

class OutputBuilder:
    """Handles output generation for scanned repositories, including multi-format support and token counts."""

    BASE_OUTPUT_DIR = (Path(__file__).parent / "../gittxt-outputs").resolve()

    def __init__(self, repo_name, output_dir=None, max_lines=None, output_format="txt"):
        """
        Initialize the OutputBuilder with output file configurations.

        :param repo_name: Name of the repository or folder being processed.
        :param output_dir: Directory where outputs will be stored (default: `gittxt-outputs/`).
        :param max_lines: Maximum number of lines per file (for large file handling).
        :param output_format: Output format(s). Can be "txt", "json", "md", or comma-separated, e.g. "txt,json".
        """
        self.output_dir = Path(output_dir).resolve() if output_dir else self.BASE_OUTPUT_DIR
        self.text_dir = self.output_dir / "text"
        self.json_dir = self.output_dir / "json"
        self.md_dir = self.output_dir / "md"
        self.max_lines = max_lines

        if "," in output_format:
            self.output_formats = [fmt.strip().lower() for fmt in output_format.split(",")]
        else:
            self.output_formats = [output_format.lower()]

        # Create directories
        for folder in [self.text_dir, self.json_dir, self.md_dir]:
            folder.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Output directory resolved to: {self.output_dir}")
        logger.debug(f"Requested output formats: {self.output_formats}")

    def generate_tree_summary(self, repo_path):
        """Generate a folder structure summary."""
        tree_str = generate_tree(Path(repo_path))
        return tree_str or "⚠️ No files found or directory empty."

    def read_file_content(self, file_path):
        """
        Read file content with optional line limits and handle missing files.
        Returns a list of lines (strings).
        """
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"⚠️ File not found: {file_path}")
            return [f"[Error: File '{file_path}' not found]\n"]

        try:
            with file_path.open("r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                return lines[:self.max_lines] if self.max_lines else lines
        except Exception as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return [f"[Error reading {file_path}: {e}]\n"]

    def _compute_token_count(self, file_content_lines):
        total_tokens = sum(len(line.strip().split()) for line in file_content_lines)
        return total_tokens

    def generate_output(self, files, repo_path, summary_data=None):
        """Generate final outputs in one or more formats."""
        tree_summary = self.generate_tree_summary(repo_path)

        if summary_data is not None:
            total_tokens = 0
            for file_path in files:
                lines = self.read_file_content(file_path)
                total_tokens += self._compute_token_count(lines)
            summary_data["estimated_tokens"] = total_tokens

        output_paths = []
        for fmt in self.output_formats:
            if fmt == "json":
                out_file = self._generate_json_output(files, tree_summary, summary_data, repo_path)
            elif fmt == "md":
                out_file = self._generate_markdown_output(files, tree_summary, summary_data, repo_path)
            else:
                out_file = self._generate_text_output(files, tree_summary, summary_data, repo_path)
            output_paths.append(str(out_file))
        return output_paths

    def _generate_text_output(self, files, tree_summary, summary_data, repo_path):
        output_file = self.text_dir / f"{self.repo_name}.txt"
        logger.info(f"📝 Writing output to {output_file} (TXT format)")
        with output_file.open("w", encoding="utf-8") as out:
            out.write(f"📂 Repository Structure Overview:\n{tree_summary}\n\n")
            if summary_data:
                out.write("📊 Summary Report:\n")
                out.write(f" - Total Files: {summary_data['total_files']}\n")
                out.write(f" - Total Size: {summary_data['total_size']} bytes\n")
                out.write(f" - File Types: {', '.join(summary_data['file_types'])}\n")
                if "estimated_tokens" in summary_data:
                    out.write(f" - Estimated Tokens: {summary_data['estimated_tokens']}\n")
                out.write("\n")
            for file_path in files:
                relative_path = str(Path(file_path).relative_to(repo_path))
                file_size = Path(file_path).stat().st_size if Path(file_path).exists() else "Unknown"
                out.write(f"=== File: {relative_path} (size: {file_size} bytes) ===\n")
                content_lines = self.read_file_content(file_path)
                out.writelines(content_lines)
                out.write("\n\n")
        logger.info(f"✅ Output saved to: {output_file}")
        return output_file

    def _generate_json_output(self, files, tree_summary, summary_data, repo_path):
        output_file = self.json_dir / f"{self.repo_name}.json"
        logger.info(f"📝 Writing output to {output_file} (JSON format)")
        output_data = {
            "repository_structure": tree_summary,
            "summary": summary_data if summary_data else {},
            "files": []
        }
        for file_path in files:
            file = Path(file_path)
            file_size = file.stat().st_size if file.exists() else "Unknown"
            content = "".join(self.read_file_content(file))
            relative_path = str(file.relative_to(repo_path))
            output_data["files"].append({
                "file": relative_path,
                "size": file_size,
                "content": content.strip()
            })
        with output_file.open("w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, indent=4)
        logger.info(f"✅ Output saved to: {output_file}")
        return output_file

    def _generate_markdown_output(self, files, tree_summary, summary_data, repo_path):
        output_file = self.md_dir / f"{self.repo_name}.md"
        logger.info(f"📝 Writing output to {output_file} (Markdown format)")
        with output_file.open("w", encoding="utf-8") as out:
            out.write(f"# 📂 Repository Overview: {self.repo_name}\n\n")
            out.write(f"## 📜 Folder Structure\n```\n{tree_summary}\n```\n\n")
            out.write("## 📊 Summary Report\n")
            if summary_data:
                out.write(f"- **Total Files Processed:** {summary_data['total_files']}\n")
                out.write(f"- **Total Size:** {summary_data['total_size']} bytes\n")
                out.write(f"- **File Types:** {', '.join(summary_data['file_types'])}\n")
                if "estimated_tokens" in summary_data:
                    out.write(f"- **Estimated Tokens:** {summary_data['estimated_tokens']}\n")
                out.write("\n")
            out.write("## 📄 Extracted Text Files\n")
            for file_path in files:
                file = Path(file_path)
                file_size = file.stat().st_size if file.exists() else "Unknown"
                relative_path = str(file.relative_to(repo_path))
                out.write(f"\n### `{relative_path}` (size: {file_size} bytes)\n")
                out.write("```plaintext\n")
                content_lines = self.read_file_content(file)
                out.writelines(content_lines)
                out.write("\n```\n")
        logger.info(f"✅ Markdown output saved to: {output_file}")
        return output_file
