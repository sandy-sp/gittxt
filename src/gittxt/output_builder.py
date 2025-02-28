import os
import json
import subprocess
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class OutputBuilder:
    """Handles output generation for scanned repositories."""

    def __init__(self, repo_name, output_dir=None, max_lines=None, output_format="txt"):
        """
        Initialize the OutputBuilder with output file configurations.

        :param repo_name: Name of the repository or folder being processed.
        :param output_dir: Directory where outputs will be stored (default: `gittxt-outputs/`).
        :param max_lines: Maximum number of lines per file (for large file handling).
        :param output_format: Output format (`txt` or `json`).
        """
        base_output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gittxt-outputs")
        self.output_dir = output_dir or base_output_dir
        self.text_dir = os.path.join(self.output_dir, "text")
        self.json_dir = os.path.join(self.output_dir, "json")
        self.max_lines = max_lines
        self.output_format = output_format.lower()
        self.repo_name = repo_name

        # Ensure output directories exist
        os.makedirs(self.text_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)

        # Determine output file path
        self.output_file = os.path.join(
            self.text_dir if self.output_format == "txt" else self.json_dir,
            f"{self.repo_name}.{self.output_format}"
        )

    def generate_tree_summary(self, repo_path):
        """Generate a folder structure summary using 'tree' command."""
        try:
            return subprocess.check_output(["tree", repo_path, "-L", "2"], text=True)
        except FileNotFoundError:
            return "⚠️ Tree command not available."

    def read_file_content(self, file_path):
        """Read file content with optional line limits and handle missing files."""
        if not os.path.exists(file_path):
            logger.error(f"⚠️ File not found: {file_path}")
            return [f"[Error: File '{file_path}' not found]\n"]

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.readlines()[:self.max_lines] if self.max_lines else f.readlines()
        except Exception as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return [f"[Error reading {file_path}: {e}]\n"]

    def generate_output(self, files, repo_path):
        """Generate the final output file in the specified format."""
        tree_summary = self.generate_tree_summary(repo_path)

        if self.output_format == "json":
            return self._generate_json_output(files, tree_summary)
        return self._generate_text_output(files, tree_summary)

    def _generate_text_output(self, files, tree_summary):
        """Generate a `.txt` file with extracted text and folder structure summary."""
        logger.info(f"📝 Writing output to {self.output_file} (TXT format)")
        with open(self.output_file, "w", encoding="utf-8") as out:
            out.write(f"📂 Repository Structure Overview:\n{tree_summary}\n\n")
            for file_path in files:
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"
                out.write(f"=== File: {file_path} (size: {file_size} bytes) ===\n")
                out.writelines(self.read_file_content(file_path))
                out.write("\n\n")
        logger.info(f"✅ Output saved to: {self.output_file}")
        return self.output_file

    def _generate_json_output(self, files, tree_summary):
        """Generate a `.json` file with structured repository content."""
        logger.info(f"📝 Writing output to {self.output_file} (JSON format)")
        output_data = {
            "repository_structure": tree_summary,
            "files": []
        }

        for file_path in files:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"
            content = "".join(self.read_file_content(file_path))
            output_data["files"].append({
                "file": file_path,
                "size": file_size,
                "content": content.strip()  # Ensure consistent formatting
            })

        with open(self.output_file, "w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, indent=4)

        logger.info(f"✅ Output saved to: {self.output_file}")
        return self.output_file
