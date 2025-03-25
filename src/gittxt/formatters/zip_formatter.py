from pathlib import Path
from zipfile import ZipFile 
from gittxt.core.logger import Logger
from gittxt.utils.github_url_utils import build_github_repo_url
import asyncio

logger = Logger.get_logger(__name__)

class ZipFormatter:
    def __init__(self, repo_name: str, output_dir: Path, output_files: list, non_textual_files: list, repo_path: Path, repo_url: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.output_files = output_files  # txt, json, md outputs
        self.non_textual_files = non_textual_files
        self.repo_path = repo_path
        self.repo_url = repo_url

    async def generate(self) -> Path:
        zip_path = self.output_dir / f"{self.repo_name}_bundle.zip"
        await asyncio.to_thread(self._create_zip, zip_path)
        return zip_path

    def _create_zip(self, zip_dest: Path):
        zip_dest.parent.mkdir(parents=True, exist_ok=True)

        with ZipFile(zip_dest, "w") as zipf:
            for output in self.output_files:
                zipf.write(output, arcname=output.name)
            zipf.writestr("README-gittxt.txt", self._get_zip_readme())
            for asset in self.non_textual_files:
                rel = asset.relative_to(self.repo_path)
                arcname = f"assets/{rel}"
                zipf.write(asset, arcname=arcname)

        if zip_dest.exists():
            logger.info(f"✅ ZIP created at {zip_dest}")
        else:
            logger.error(f"❌ Failed to create ZIP at {zip_dest}")

    def _get_zip_readme(self) -> str:
        repo_link = build_github_repo_url(self.repo_url)
        url_line = f"Repository URL: {repo_link}\n" if repo_link else ""
        return (
            f"Gittxt Export Bundle for {self.repo_name}\n"
            "===================================\n"
            "\n"
            f"{url_line}"
            "Includes:\n"
            "- Extracted text files: .txt, .json, .md\n"
            "- Assets placed under /assets/ folder preserving structure\n"
            "\n"
            "Generated by Gittxt AI tooling\n"
        )
