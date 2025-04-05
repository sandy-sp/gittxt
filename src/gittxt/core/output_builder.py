from pathlib import Path
import asyncio
import re
import hashlib
from urllib.parse import urlparse
from gittxt.core.logger import Logger
from gittxt.core.constants import TEXT_DIR, JSON_DIR, MD_DIR, ZIP_DIR
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.summary_utils import generate_summary
from gittxt.formatters.text_formatter import TextFormatter
from gittxt.formatters.json_formatter import JSONFormatter
from gittxt.formatters.markdown_formatter import MarkdownFormatter
from gittxt.formatters.zip_formatter import ZipFormatter

logger = Logger.get_logger(__name__)


class OutputBuilder:
    VALID_FORMATS = {"txt", "json", "md"}
    VALID_MODES = {"rich", "lite"}

    FORMATTERS = {
        "txt": TextFormatter,
        "json": JSONFormatter,
        "md": MarkdownFormatter,
    }

    def __init__(
        self,
        repo_name,
        output_dir,
        output_format="txt",
        repo_url=None,
        branch=None,
        subdir=None,
        mode="rich",
    ):
        self.repo_name = repo_name
        self.repo_url = repo_url or ""
        self.branch = branch
        self.subdir = subdir
        self.mode = mode.lower()
        self.output_dir = Path(output_dir).resolve()
        if isinstance(output_format, str):
            self.output_formats = [
                fmt.strip().lower() for fmt in output_format.split(",")
            ]
        elif isinstance(output_format, list):
            self.output_formats = [fmt.strip().lower() for fmt in output_format]
        else:
            raise TypeError(f"Invalid output_format type: {type(output_format)}")
        self.repo_path = None

        # Validate mode and formats
        if self.mode not in self.VALID_MODES:
            raise ValueError(
                f"Invalid mode: '{self.mode}'. Must be one of: {', '.join(self.VALID_MODES)}"
            )
        for fmt in self.output_formats:
            if fmt not in self.VALID_FORMATS:
                raise ValueError(
                    f"Unsupported output format: '{fmt}'. Allowed: {', '.join(self.VALID_FORMATS)}"
                )

        self.directories = {
            "txt": self.output_dir / TEXT_DIR,
            "json": self.output_dir / JSON_DIR,
            "md": self.output_dir / MD_DIR,
            "zip": self.output_dir / ZIP_DIR,
        }
        for folder in self.directories.values():
            folder.mkdir(parents=True, exist_ok=True)

    def _get_dynamic_basename(self):
        def sanitize(name):
            return re.sub(r"[^a-zA-Z0-9]", "_", name)

        def truncate_or_hash(name, max_len=50):
            if len(name) > max_len:
                suffix = hashlib.md5(name.encode()).hexdigest()[:8]
                return f"{name[:max_len - 9]}_{suffix}"
            return name

        base_name = self.repo_name

        if self.repo_url and self.repo_url.startswith("http"):
            # GitHub URL
            parsed_url = urlparse(self.repo_url)
            parts = Path(parsed_url.path).parts
            if "tree" in parts:
                tree_idx = parts.index("tree")
                subdir_parts = parts[tree_idx + 2 :]  # skip 'tree' and branch
                if subdir_parts:
                    base_name = f"{base_name}_{'_'.join(subdir_parts)}"
        elif self.repo_url:
            # Local path
            local_root = Path(self.repo_url).resolve()
            base_name = local_root.parts[-1]

        return truncate_or_hash(sanitize(base_name))

    def _generate_file_metadata(self, file_path, repo_path):
        """
        Generate metadata for a single file.
        """
        # Adjust relative path to include subdir if applicable
        relative_path = file_path.relative_to(repo_path)
        if self.subdir:
            github_path = f"{self.subdir.rstrip('/')}/{relative_path.as_posix()}"
        else:
            github_path = relative_path.as_posix()

        return {
            "raw_url": f"{self.repo_url}/blob/{self.branch}/{github_path}",
        }

    async def generate_output(
        self,
        textual_files,
        non_textual_files,
        repo_path,
        create_zip=False,
        tree_depth=None,
    ):
        self.repo_path = Path(repo_path).resolve()
        root_for_tree = self.repo_path / self.subdir if self.subdir else self.repo_path
        tree_summary = generate_tree(root_for_tree, max_depth=tree_depth)
        summary_data = await generate_summary(textual_files + non_textual_files)

        output_files = []
        tasks = []

        for fmt in self.output_formats:
            FormatterClass = self.FORMATTERS.get(fmt)
            if not FormatterClass:
                logger.warning(f"⚠️ Unsupported formatter: {fmt}")
                continue

            formatter = FormatterClass(
                repo_name=self._get_dynamic_basename(),
                output_dir=self.directories[fmt],
                repo_path=self.repo_path,
                tree_summary=tree_summary,
                repo_url=self.repo_url,
                branch=self.branch,
                subdir=self.subdir,
                mode=self.mode,
            )

            tasks.append(
                formatter.generate(
                    text_files=textual_files,
                    non_textual_files=non_textual_files,
                    summary_data=summary_data,
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"❌ Formatter failed: {result}")
            elif result:
                output_files.append(result)
                logger.info(f"📄 Output generated: {result}")

        if create_zip:
            full_output_files = []
            for fmt in self.output_formats:
                FormatterClass = self.FORMATTERS[fmt]
                formatter = FormatterClass(
                    repo_name=self._get_dynamic_basename(),
                    output_dir=self.directories[fmt],
                    repo_path=self.repo_path,
                    tree_summary=tree_summary,
                    repo_url=self.repo_url,
                    branch=self.branch,
                    subdir=self.subdir,
                    mode=self.mode,
                )
                try:
                    result = await formatter.generate(
                        text_files=textual_files,
                        non_textual_files=non_textual_files,
                        summary_data=summary_data,
                    )
                    if result:
                        full_output_files.append(result)
                except Exception as e:
                    logger.error(f"❌ Formatter {fmt} failed for ZIP bundle: {e}")

            zip_formatter = ZipFormatter(
                repo_name=self._get_dynamic_basename(),
                output_dir=self.directories["zip"],
                output_files=full_output_files,
                non_textual_files=non_textual_files,
                repo_path=self.repo_path,
                repo_url=self.repo_url,
            )
            zip_path = await zip_formatter.generate()
            if zip_path:
                output_files.append(zip_path)
                logger.info(f"📦 Zipped bundle created: {zip_path}")

        return output_files
