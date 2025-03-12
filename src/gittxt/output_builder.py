import os
import json
import re
import subprocess
from typing import List
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

class OutputBuilder:
    """Handles output generation for scanned repositories, including multi-format support and token counts."""

    BASE_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs"))

    def __init__(self, repo_name, output_dir=None, max_lines=None, output_format="txt"):
        """
        Initialize the OutputBuilder with output file configurations.

        :param repo_name: Name of the repository or folder being processed.
        :param output_dir: Directory where outputs will be stored (default: `gittxt-outputs/`).
        :param max_lines: Maximum number of lines per file (for large file handling).
        :param output_format: Output format(s). Can be "txt", "json", "md", or comma-separated, e.g. "txt,json".
        """
        # Ensure absolute path for output directory
        self.output_dir = os.path.abspath(output_dir) if output_dir else self.BASE_OUTPUT_DIR
        self.text_dir = os.path.join(self.output_dir, "text")
        self.json_dir = os.path.join(self.output_dir, "json")
        self.md_dir = os.path.join(self.output_dir, "md")  # Directory for markdown output
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

    def generate_tree_summary(self, repo_path):
        """Generate a folder structure summary using 'tree' command."""
        try:
            return subprocess.check_output(["tree", repo_path], text=True)
        except FileNotFoundError:
            logger.warning("⚠️ Tree command not found, skipping repository structure summary.")
            return "⚠️ Tree command not available."
        except Exception as e:
            logger.error(f"❌ Error generating tree summary: {e}")
            return "⚠️ Error generating repository structure."

    def read_file_content(self, file_path):
        """
        Read file content with optional line limits and handle missing files.
        Returns a list of lines (strings).
        """
        if not os.path.exists(file_path):
            logger.error(f"⚠️ File not found: {file_path}")
            return [f"[Error: File '{file_path}' not found]\n"]

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                return lines[:self.max_lines] if self.max_lines else lines
        except Exception as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return [f"[Error reading {file_path}: {e}]\n"]

    def _compute_token_count(self, file_content_lines: List[str]) -> int:
        """
        Compute a more accurate token count estimation for LLM processing.
        This implementation follows common tokenization patterns used by LLMs.
        
        Args:
            file_content_lines: List of strings, each representing a line of text
        
        Returns:
            int: Estimated number of tokens
        """
        def split_into_tokens(text: str) -> List[str]:
            # Handle common code and text patterns
            patterns = [
                r'[A-Za-z]+(?:[A-Z][a-z]+)*',  # CamelCase and words
                r'\d+(?:\.\d+)?',              # Numbers including decimals
                r'[^\w\s]+',                   # Special characters and punctuation
                r'[\n\t]+',                    # New lines and tabs
                r'\s+'                         # Whitespace
            ]
            pattern = '|'.join(f'({p})' for p in patterns)
            return [token for token in re.findall(pattern, text) if any(token)]

        total_tokens = 0
        for line in file_content_lines:
            # Process each line
            tokens = split_into_tokens(line)
            
            # Additional token counting rules
            for token in tokens:
                # Base token count
                token_count = 1
                
                # Adjust for longer tokens that might be split further by LLM
                if len(token) > 12:  # Most LLMs split long tokens
                    token_count += len(token) // 8  # Approximate subword tokenization
                
                # Account for special tokens
                if token.strip() in {'\n', '\t', ' '}:
                    token_count = 1  # Count whitespace as single tokens
                
                total_tokens += token_count

        # Add a small overhead for special tokens (e.g., BOS, EOS)
        total_tokens += 2
        
        return total_tokens

    def generate_output(self, files, repo_path, summary_data=None):
        """
        Generate final outputs in one or more formats.
        Returns a list of output file paths.
        """
        tree_summary = self.generate_tree_summary(repo_path)

        # Compute naive token count across all files if summary_data is provided
        if summary_data is not None:
            total_tokens = 0
            for file_path in files:
                lines = self.read_file_content(file_path)
                total_tokens += self._compute_token_count(lines)
            summary_data["estimated_tokens"] = total_tokens

        output_paths = []
        # For each requested format, call the specialized generator
        for fmt in self.output_formats:
            if fmt == "json":
                out_file = self._generate_json_output(files, tree_summary, summary_data, repo_path)
            elif fmt == "md":
                out_file = self._generate_markdown_output(files, tree_summary, summary_data, repo_path)
            else:
                # Default to txt if unknown or "txt" is specified
                out_file = self._generate_text_output(files, tree_summary, summary_data, repo_path)
            output_paths.append(out_file)
        return output_paths

    def _generate_text_output(self, files, tree_summary, summary_data, repo_path):
        """Generate a `.txt` file with extracted text and folder structure summary."""
        output_file = os.path.join(self.text_dir, f"{self.repo_name}.txt")
        logger.info(f"📝 Writing output to {output_file} (TXT format)")
        with open(output_file, "w", encoding="utf-8") as out:
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
                # Compute relative path from repository root to sanitize output.
                relative_path = os.path.relpath(file_path, repo_path)
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"
                out.write(f"=== File: {relative_path} (size: {file_size} bytes) ===\n")
                content_lines = self.read_file_content(file_path)
                out.writelines(content_lines)
                out.write("\n\n")
        logger.info(f"✅ Output saved to: {output_file}")
        return output_file

    def _generate_json_output(self, files, tree_summary, summary_data, repo_path):
        """Generate a `.json` file with structured repository content."""
        output_file = os.path.join(self.json_dir, f"{self.repo_name}.json")
        logger.info(f"📝 Writing output to {output_file} (JSON format)")
        output_data = {
            "repository_structure": tree_summary,
            "summary": summary_data if summary_data else {},
            "files": []
        }
        for file_path in files:
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"
            content = "".join(self.read_file_content(file_path))
            relative_path = os.path.relpath(file_path, repo_path)
            output_data["files"].append({
                "file": relative_path,
                "size": file_size,
                "content": content.strip()
            })
        try:
            with open(output_file, "w", encoding="utf-8") as json_file:
                json.dump(output_data, json_file, indent=4)
        except TypeError as e:
            logger.error(f"❌ Error saving JSON output: {e}")
        logger.info(f"✅ Output saved to: {output_file}")
        return output_file

    def _generate_markdown_output(self, files, tree_summary, summary_data, repo_path):
        """Generate a `.md` file with structured repository content."""
        output_file = os.path.join(self.md_dir, f"{self.repo_name}.md")
        logger.info(f"📝 Writing output to {output_file} (Markdown format)")
        with open(output_file, "w", encoding="utf-8") as out:
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
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else "Unknown"
                relative_path = os.path.relpath(file_path, repo_path)
                out.write(f"\n### `{relative_path}` (size: {file_size} bytes)\n")
                out.write("```plaintext\n")
                content_lines = self.read_file_content(file_path)
                out.writelines(content_lines)
                out.write("\n```\n")
        logger.info(f"✅ Markdown output saved to: {output_file}")
        return output_file
