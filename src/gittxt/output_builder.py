from pathlib import Path
import asyncio
from gittxt.logger import Logger
from gittxt.utils.tree_utils import generate_tree
from gittxt.formatters.text_formatter import TextFormatter
from gittxt.formatters.json_formatter import JSONFormatter
from gittxt.formatters.markdown_formatter import MarkdownFormatter
from gittxt.formatters.zip_formatter import ZipFormatter

logger = Logger.get_logger(__name__)

class OutputBuilder:
    """Handles output generation for scanned repositories via formatter strategies."""

    BASE_OUTPUT_DIR = (Path(__file__).parent / "../gittxt-outputs").resolve()

    FORMATTERS = {
        "txt": TextFormatter,
        "json": JSONFormatter,
        "md": MarkdownFormatter,
    }

    def __init__(self, repo_name, output_dir=None, output_format="txt"):
        self.repo_name = repo_name
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

        # Separate TEXTUAL and NON-TEXTUAL buckets
        textual_files = [f for f in all_files if self._is_textual(f)]
        non_textual_files = [f for f in all_files if not self._is_textual(f)]

        output_files = []
        tasks = []
        for fmt in self.output_formats:
            FormatterClass = self.FORMATTERS.get(fmt)
            if FormatterClass:
                formatter = FormatterClass(
                    repo_name=self.repo_name,
                    output_dir=self.directories[fmt],
                    repo_path=repo_path,
                    tree_summary=tree_summary,
                )
                tasks.append(formatter.generate(textual_files, non_textual_files))

        generated_outputs = await asyncio.gather(*tasks)
        for out in generated_outputs:
            logger.info(f"📄 Output ready at: {out}")
            output_files.append(out)

        if create_zip:
            zip_formatter = ZipFormatter(
                repo_name=self.repo_name,
                output_dir=self.directories["zip"],
                output_files=output_files,
                non_textual_files=non_textual_files,
            )
            zip_path = await zip_formatter.generate()
            logger.info(f"📦 Zipped bundle created: {zip_path}")
            output_files.append(zip_path)

        return output_files

    def _is_textual(self, file: Path) -> bool:
        from gittxt.utils.filetype_utils import classify_simple
        primary, _ = classify_simple(file)
        return primary == "TEXTUAL"
