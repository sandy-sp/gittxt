from pathlib import Path
import asyncio
from gittxt.logger import Logger
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.filetype_utils import classify_file
from gittxt.formatters.text_formatter import TextFormatter
from gittxt.formatters.json_formatter import JSONFormatter
from gittxt.formatters.markdown_formatter import MarkdownFormatter

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

    async def generate_output(self, files, repo_path, create_zip=False, tree_depth=None):
        tree_summary = generate_tree(Path(repo_path), max_depth=tree_depth)

        text_files = []
        asset_files = []
        output_files = []

        for file in files:
            file_type = classify_file(file)
            if file_type in {"code", "docs", "csv"}:
                text_files.append(file)
            elif file_type in {"image", "media", "asset"}:
                asset_files.append(file)

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
                tasks.append(formatter.generate(text_files, asset_files))

        generated_outputs = await asyncio.gather(*tasks)
        for out in generated_outputs:
            logger.info(f"📄 Output ready at: {out}")
            output_files.append(out)

        if create_zip:
            logger.info(f"📦 Creating ZIP at: {self.directories['zip'] / f'{self.repo_name}_bundle.zip'}")
            zip_path = self.directories["zip"] / f"{self.repo_name}_bundle.zip"
            files_to_zip = [(file, repo_path) for file in output_files + asset_files]
            await asyncio.to_thread(self._zip_with_relative_paths, files_to_zip, zip_path)
            logger.info(f"📦 Zipped bundle created: {zip_path}")

        return text_files

    def _zip_with_relative_paths(self, file_repo_pairs, zip_dest: Path):
        from zipfile import ZipFile
        zip_dest.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(zip_dest, "w") as zipf:
            for file, base in file_repo_pairs:
                try:
                    arcname = file.relative_to(base)
                except ValueError:
                    arcname = file.name
                zipf.write(file, arcname=arcname)
        if zip_dest.exists():
            logger.warning(f"⚠️ ZIP file {zip_dest} already exists and will be overwritten.")
