import asyncio
from pathlib import Path
from gittxt.core.logger import Logger
from gittxt.core.constants import TEXT_DIR, JSON_DIR, MD_DIR, ZIP_DIR
from gittxt.utils.tree_utils import generate_tree
from gittxt.formatters.text_formatter import TextFormatter
from gittxt.formatters.json_formatter import JSONFormatter
from gittxt.formatters.markdown_formatter import MarkdownFormatter
from gittxt.formatters.zip_formatter import ZipFormatter
from gittxt.utils.filetype_utils import classify_file
from gittxt.utils.summary_utils import generate_summary

logger = Logger.get_logger(__name__)

class OutputBuilder:
    FORMATTERS = {
        "txt": TextFormatter,
        "json": JSONFormatter,
        "md": MarkdownFormatter,
    }

    def __init__(self, repo_name, output_dir, output_format="txt", repo_url=None, branch=None, subdir=None):
        self.repo_name = repo_name
        self.repo_url = repo_url
        self.branch = branch
        self.subdir = subdir
        self.output_dir = Path(output_dir).resolve()
        self.output_formats = [fmt.strip().lower() for fmt in output_format.split(",")]

        self.directories = {
            "txt": self.output_dir / TEXT_DIR,
            "json": self.output_dir / JSON_DIR,
            "md": self.output_dir / MD_DIR,
            "zip": self.output_dir / ZIP_DIR,
        }
        for folder in self.directories.values():
            folder.mkdir(parents=True, exist_ok=True)

    async def generate_output(self, all_files, repo_path, create_zip=False, tree_depth=None, mode="rich"):
        tree_summary = generate_tree(Path(repo_path), max_depth=tree_depth)

        # Classify once
        textual_files, non_textual_files = [], []
        for f in all_files:
            if classify_file(f) == "TEXTUAL":
                textual_files.append(f)
            else:
                non_textual_files.append(f)

        # Central summary (tokens, size, breakdowns, formatted)
        summary_data = await generate_summary(textual_files + non_textual_files)

        output_files = []
        tasks = []

        for fmt in self.output_formats:
            FormatterClass = self.FORMATTERS.get(fmt)
            if not FormatterClass:
                logger.warning(f"⚠️ Unsupported formatter: {fmt}")
                continue

            formatter = FormatterClass(
                repo_name=self.repo_name,
                output_dir=self.directories[fmt],
                repo_path=repo_path,
                tree_summary=tree_summary,
                repo_url=self.repo_url,
                branch=self.branch,
                subdir=self.subdir
            )

            tasks.append(formatter.generate(
                text_files=textual_files,
                non_textual_files=non_textual_files,
                summary_data=summary_data,
                mode=mode
            ))

        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                output_files.append(result)
                logger.info(f"📄 Output generated: {result}")

        if create_zip:
            zip_formatter = ZipFormatter(
                repo_name=self.repo_name,
                output_dir=self.directories["zip"],
                output_files=output_files,
                non_textual_files=non_textual_files,
                repo_path=repo_path,
                repo_url=self.repo_url
            )
            zip_path = await zip_formatter.generate()
            if zip_path:
                output_files.append(zip_path)
                logger.info(f"📦 Zipped bundle created: {zip_path}")

        return output_files
