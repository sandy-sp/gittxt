import os
import json
import aiofiles
import asyncio
import subprocess
from gittxt.logger import Logger
from gittxt.utils import get_file_extension, normalize_path
from gittxt.config import ConfigManager

logger = Logger.get_logger(__name__)

class OutputBuilder:
    """Handles output generation for scanned repositories, including multi-format support and token counts."""

    BASE_OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../gittxt-outputs"))

    def __init__(self, repo_name, output_dir=None, output_format="txt"):
        """
        Initialize the OutputBuilder with output file configurations.

        :param repo_name: Name of the repository or folder being processed.
        :param output_dir: Directory where outputs will be stored (default: `gittxt-outputs/`).
        :param output_format: Output format(s). Can be "txt", "json", "md", "yaml", or comma-separated formats.
        """
        self.output_dir = normalize_path(output_dir) if output_dir else self.BASE_OUTPUT_DIR
        self.text_dir = os.path.join(self.output_dir, "text")
        self.json_dir = os.path.join(self.output_dir, "json")
        self.md_dir = os.path.join(self.output_dir, "md")
        self.yaml_dir = os.path.join(self.output_dir, "yaml")
        
        # Allow multiple output formats
        if "," in output_format:
            self.output_formats = [fmt.strip().lower() for fmt in output_format.split(",")]
        else:
            self.output_formats = [output_format.lower()]

        self.repo_name = repo_name

        # Ensure output directories exist
        for directory in [self.text_dir, self.json_dir, self.md_dir, self.yaml_dir]:
            os.makedirs(directory, exist_ok=True)

        logger.debug(f"Output directory resolved to: {self.output_dir}")
        logger.debug(f"Requested output formats: {self.output_formats}")

    async def generate_tree_summary(self, repo_path):
        """Generate a folder structure summary using 'tree' command asynchronously."""
        try:
            return await asyncio.create_subprocess_shell(
                f"tree {repo_path}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
        except FileNotFoundError:
            logger.warning("⚠️ Tree command not found, skipping repository structure summary.")
            return "⚠️ Tree command not available."
        except Exception as e:
            logger.error(f"❌ Error generating tree summary: {e}")
            return "⚠️ Error generating repository structure."

    async def read_file_content(self, file_path):
        """Read file content asynchronously."""
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return await f.readlines()
        except Exception as e:
            logger.error(f"❌ Error reading {file_path}: {e}")
            return []

    async def generate_output(self, files, repo_path, summary_data=None):
        """Generate outputs in specified formats asynchronously."""
        tree_summary = await self.generate_tree_summary(repo_path)
        
        # Compute token count
        total_tokens = sum(len((await self.read_file_content(f))) for f in files)
        if summary_data:
            summary_data["estimated_tokens"] = total_tokens

        output_paths = []
        for fmt in self.output_formats:
            if fmt == "json":
                out_file = await self._generate_json_output(files, tree_summary, summary_data, repo_path)
            elif fmt == "md":
                out_file = await self._generate_markdown_output(files, tree_summary, summary_data, repo_path)
            elif fmt == "yaml":
                out_file = await self._generate_yaml_output(files, tree_summary, summary_data, repo_path)
            else:
                out_file = await self._generate_text_output(files, tree_summary, summary_data, repo_path)
            output_paths.append(out_file)
        return output_paths

    async def _generate_text_output(self, files, tree_summary, summary_data, repo_path):
        """Generate a `.txt` output file."""
        output_file = os.path.join(self.text_dir, f"{self.repo_name}.txt")
        async with aiofiles.open(output_file, "w", encoding="utf-8") as out:
            await out.write(f"📂 Repository Structure Overview:\n{tree_summary}\n\n")
            if summary_data:
                await out.write(json.dumps(summary_data, indent=4))
                await out.write("\n")
        return output_file

    async def _generate_json_output(self, files, tree_summary, summary_data, repo_path):
        """Generate a `.json` output file."""
        output_file = os.path.join(self.json_dir, f"{self.repo_name}.json")
        output_data = {
            "repository_structure": tree_summary,
            "summary": summary_data if summary_data else {},
            "files": []
        }
        for file_path in files:
            content = await self.read_file_content(file_path)
            output_data["files"].append({
                "file": os.path.relpath(file_path, repo_path),
                "size": os.path.getsize(file_path),
                "content": "".join(content).strip()
            })
        async with aiofiles.open(output_file, "w", encoding="utf-8") as json_file:
            await json_file.write(json.dumps(output_data, indent=4))
        return output_file

    async def _generate_markdown_output(self, files, tree_summary, summary_data, repo_path):
        """Generate a `.md` output file."""
        output_file = os.path.join(self.md_dir, f"{self.repo_name}.md")
        async with aiofiles.open(output_file, "w", encoding="utf-8") as out:
            await out.write(f"# 📂 Repository Overview: {self.repo_name}\n\n")
            await out.write(f"## 📜 Folder Structure\n```\n{tree_summary}\n```\n\n")
            await out.write("## 📊 Summary Report\n")
            if summary_data:
                await out.write(json.dumps(summary_data, indent=4))
                await out.write("\n")
        return output_file

    async def _generate_yaml_output(self, files, tree_summary, summary_data, repo_path):
        """Generate a `.yaml` output file."""
        import yaml
        output_file = os.path.join(self.yaml_dir, f"{self.repo_name}.yaml")
        output_data = {
            "repository_structure": tree_summary,
            "summary": summary_data if summary_data else {},
            "files": [os.path.relpath(f, repo_path) for f in files]
        }
        async with aiofiles.open(output_file, "w", encoding="utf-8") as yaml_file:
            await yaml_file.write(yaml.dump(output_data))
        return output_file
