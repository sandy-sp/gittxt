from pathlib import Path
import asyncio
from gittxt.core.logger import Logger
from gittxt.utils.tree_utils import generate_tree
from gittxt.formatters.text_formatter import TextFormatter
from gittxt.formatters.json_formatter import JSONFormatter
from gittxt.formatters.markdown_formatter import MarkdownFormatter
from gittxt.formatters.zip_formatter import ZipFormatter
from gittxt.utils.filetype_utils import classify_simple

logger = Logger.get_logger(__name__)

class OutputBuilder:
    """Handles output generation for scanned repositories via formatter strategies."""

    BASE_OUTPUT_DIR = (Path(__file__).parent / "../gittxt-outputs").resolve()

    FORMATTERS = {
        "txt": TextFormatter,
        "json": JSONFormatter,
        "md": MarkdownFormatter,
    }

    def __init__(self, repo_name, output_dir=None, output_format="txt", repo_url=None):
        self.repo_name = repo_name
        self.repo_url = repo_url
        self.output_dir = Path(output_dir).resolve() if output_dir else self.BASE_OUTPUT_DIR
        self.output_formats = [fmt.strip().lower() for fmt in output_format.split(",")]

        self.directories = {
            "txt": self.output_dir / "text",
            "json": self.output_dir / "json",
            "md": self.output_dir / "md",
            "zip": self.output_dir / "zips",
        }
        for folder in self.directories.values():
            folder.mkdir(parents=True, exist_ok=True)

    async def generate_output(self, all_files, repo_path, create_zip=False, tree_depth=None):
        tree_summary = generate_tree(Path(repo_path), max_depth=tree_depth)

        # Avoid running classify_simple() twice
        file_groups = {
            "textual": [],
            "non_textual": []
        }
        for f in all_files:
            primary, _ = classify_simple(f)
            if primary == "TEXTUAL":
                file_groups["textual"].append(f)
            else:
                file_groups["non_textual"].append(f)

        output_files = []
        tasks = []

        # Formatter tasks
        for fmt in self.output_formats:
            FormatterClass = self.FORMATTERS.get(fmt)
            if FormatterClass:
                formatter = FormatterClass(
                    repo_name=self.repo_name,
                    output_dir=self.directories[fmt],
                    repo_path=repo_path,
                    tree_summary=tree_summary,
                    repo_url=self.repo_url
                )
                tasks.append(formatter.generate(file_groups["textual"], file_groups["non_textual"]))

        # ZIP bundle task (runs concurrently)
        if create_zip:
            zip_formatter = ZipFormatter(
                repo_name=self.repo_name,
                output_dir=self.directories["zip"],
                output_files=[],  # Placeholder, populated post-formatters
                non_textual_files=file_groups["non_textual"],
                repo_path=repo_path,
                repo_url=self.repo_url
            )
            # Attach to the event loop after formatters
            async def zip_task():
                generated_outputs = await asyncio.gather(*tasks)
                for out in generated_outputs:
                    logger.info(f"📄 Output ready at: {out}")
                output_files.extend(generated_outputs)
                zip_formatter.output_files = output_files.copy()
                zip_path = await zip_formatter.generate()
                logger.info(f"📦 Zipped bundle created: {zip_path}")
                output_files.append(zip_path)
                return output_files

            return await zip_task()

        # Normal non-zip workflow
        generated_outputs = await asyncio.gather(*tasks)
        for out in generated_outputs:
            logger.info(f"📄 Output ready at: {out}")
            output_files.append(out)

        return output_files
