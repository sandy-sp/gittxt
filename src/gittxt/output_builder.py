import os
import json
import subprocess
from gittxt.logger import get_logger

logger = get_logger(__name__)

# Define the directory structure for output storage inside `src/gittxt-outputs/`
SRC_DIR = os.path.dirname(__file__)  # `src/gittxt/`
OUTPUT_DIR = os.path.join(SRC_DIR, "../gittxt-outputs")  # `src/gittxt-outputs/`
TEXT_DIR = os.path.join(OUTPUT_DIR, "text")  # `src/gittxt-outputs/text/`
JSON_DIR = os.path.join(OUTPUT_DIR, "json")  # `src/gittxt-outputs/json/`

# Ensure directories exist
os.makedirs(TEXT_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)

class OutputBuilder:
    def __init__(self, repo_name, max_lines=None, output_format="txt"):
        """Initialize the OutputBuilder class with repository name and output format."""
        self.repo_name = repo_name
        self.max_lines = max_lines
        self.output_format = output_format.lower()
        
        # Fix naming for local directories (avoid "..txt" issue)
        if self.repo_name in [".", ".."]:
            self.repo_name = "current_directory"

        # Set output file path based on format
        self.output_file = os.path.join(
            TEXT_DIR if self.output_format == "txt" else JSON_DIR,
            f"{self.repo_name}.{self.output_format}"
        )

    def read_file_content(self, file_path):
        """Read file content with optional line limits, handling missing files."""
        if not os.path.exists(file_path):
            logger.warning(f"Skipping missing file: {file_path}")
            return [f"[Warning: Missing file: {file_path}]\n"]
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.readlines()[:self.max_lines] if self.max_lines else f.readlines()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return [f"[Error reading {file_path}: {e}]\n"]

    def generate_tree_summary(self, repo_path):
        """Generate a folder structure summary using 'tree'."""
        try:
            return subprocess.check_output(["tree", repo_path, "-L", "2"], text=True)
        except FileNotFoundError:
            return "Tree command not available."

    def generate_output(self, files, repo_path):
        """Generate the final output file in the specified format."""
        tree_summary = self.generate_tree_summary(repo_path)

        if self.output_format == "json":
            return self._generate_json_output(files, tree_summary)
        return self._generate_text_output(files, tree_summary)

    def _generate_text_output(self, files, tree_summary):
        """Generate a `.txt` file with extracted text and tree summary."""
        logger.info(f"Writing output to {self.output_file} (TXT format)")
        with open(self.output_file, "w", encoding="utf-8") as out:
            out.write(f"Repository Structure Overview:\n{tree_summary}\n\n")
            for file_path in files:
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"
                out.write(f"=== File: {file_path} (size: {file_size} bytes) ===\n")
                out.writelines(self.read_file_content(file_path))
                out.write("\n\n")
        logger.info(f"✅ Output saved to {self.output_file}")
        return self.output_file

    def _generate_json_output(self, files, tree_summary):
        """Generate a `.json` file with structured output while avoiding excessive size."""
        logger.info(f"Writing output to {self.output_file} (JSON format)")
        output_data = {
            "repository_structure": tree_summary,
            "files": []
        }

        for file_path in files:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"

            # Limit the amount of text stored in JSON output
            file_content = self.read_file_content(file_path)
            content = "".join(file_content) if len(file_content) < 500 else "[Content too large to display]"

            output_data["files"].append({
                "file": file_path,
                "size": file_size,
                "content": content
            })

        with open(self.output_file, "w", encoding="utf-8") as json_file:
            json.dump(output_data, json_file, indent=4)
        
        logger.info(f"✅ Output saved to {self.output_file}")
        return self.output_file
