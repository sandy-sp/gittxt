import os
import json
import subprocess
from gittxt.logger import Logger
from gittxt.config import ConfigManager

logger = Logger.get_logger(__name__)

class OutputBuilder:
    """Handles output generation for scanned repositories, ensuring a unified processed directory."""

    config = ConfigManager.load_config()
    BASE_OUTPUT_DIR = config["output_dir"]  # Unified processed output directory

    def __init__(self, repo_name, max_lines=None, output_format="txt"):
        """
        Initialize the OutputBuilder with output file configurations.

        :param repo_name: Name of the repository or folder being processed.
        :param max_lines: Maximum number of lines per file (for large file handling).
        :param output_format: Output format(s). Can be "txt", "json", "md", or comma-separated, e.g. "txt,json".
        """
        self.output_dir = self.BASE_OUTPUT_DIR
        self.text_dir = os.path.join(self.output_dir, "text")
        self.json_dir = os.path.join(self.output_dir, "json")
        self.md_dir = os.path.join(self.output_dir, "md")
        self.max_lines = max_lines

        # If multiple formats are specified, parse them; otherwise, store as single
        if "," in output_format:
            self.output_formats = [fmt.strip().lower() for fmt in output_format.split(",")]
        else:
            self.output_formats = [output_format.lower()]

        self.repo_name = repo_name

        # Ensure output directories exist
        os.makedirs(self.text_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.md_dir, exist_ok=True)

        logger.debug(f"Output directory resolved to: {self.output_dir}")
        logger.debug(f"Requested output formats: {self.output_formats}")

    def generate_output(self, files, repo_path, summary_data=None):
        """
        Generate final outputs in one or more formats.
        Returns a list of output file paths.
        """
        output_paths = []
        base_output_path = os.path.join(self.output_dir, self.repo_name)
        os.makedirs(base_output_path, exist_ok=True)

        for fmt in self.output_formats:
            if fmt == "json":
                out_file = self._generate_json_output(files, summary_data, base_output_path)
            elif fmt == "md":
                out_file = self._generate_markdown_output(files, summary_data, base_output_path)
            else:
                out_file = self._generate_text_output(files, summary_data, base_output_path)

            output_paths.append(out_file)
        return output_paths

    def _generate_text_output(self, files, summary_data, repo_path):
        """Generate a `.txt` file with extracted text."""
        output_file = os.path.join(self.text_dir, f"{self.repo_name}.txt")
        with open(output_file, "w", encoding="utf-8") as out:
            if summary_data:
                out.write(f"📊 Summary Report:\n - Total Files: {summary_data['total_files']}\n")
            for file_path in files:
                relative_path = os.path.relpath(file_path, repo_path)
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"
                out.write(f"=== File: {relative_path} (size: {file_size} bytes) ===\n")
                content_lines = self.read_file_content(file_path)
                out.writelines(content_lines)
                out.write("\n\n")
        return output_file

    def _generate_json_output(self, files, summary_data, repo_path):
        """Generate a `.json` file with structured repository content."""
        output_file = os.path.join(self.json_dir, f"{self.repo_name}.json")
        output_data = {"summary": summary_data if summary_data else {}, "files": []}
        for file_path in files:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"
            content = "".join(self.read_file_content(file_path))
            relative_path = os.path.relpath(file_path, repo_path)
            output_data["files"].append({"file": relative_path, "size": file_size, "content": content.strip()})
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, indent=4)
        return output_file

    def _generate_markdown_output(self, files, summary_data, output_path):
        """Generate a `.md` file with structured repository content."""
        output_file = os.path.join(output_path, f"{self.repo_name}.md")
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(f"# 📂 Repository Overview: {self.repo_name}\n\n")
            if summary_data:
                out.write(f"- **Total Files:** {summary_data['total_files']}\n")
            for file_path in files:
                filename = os.path.basename(file_path)
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"
                out.write(f"\n### `{filename}` (size: {file_size} bytes)\n\n")
                content_lines = self.read_file_content(file_path)
                out.writelines(content_lines)
                out.write("\n")
        return output_file
