import shutil
from pathlib import Path
from datetime import datetime, timezone
import aiofiles
import zipfile


class ZipFormatter:
    def __init__(self, repo_name, output_dir: Path, output_files: list, non_textual_files: list, repo_path: Path, repo_url: str = None, branch: str = None, subdir: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.output_files = output_files
        self.non_textual_files = non_textual_files
        self.repo_path = repo_path
        self.repo_url = repo_url
        self.branch = branch
        self.subdir = subdir

    async def generate(self):
        if not self.output_files:
            return None

        zip_path = self.output_dir / f"{self.repo_name}.zip"
        assets_dir = self.output_dir / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Copy non-textual assets to local temp dir
        copied_assets = []
        for asset in self.non_textual_files:
            rel_path = asset.relative_to(self.repo_path)
            dest_path = assets_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(asset, dest_path)
            copied_assets.append((dest_path, rel_path))

        # Create optional README
        readme_path = self.output_dir / "README.txt"
        async with aiofiles.open(readme_path, "w", encoding="utf-8") as f:
            await f.write(f"Gittxt Archive for {self.repo_name}\n")
            await f.write(f"Generated: {datetime.now(timezone.utc).isoformat()} UTC\n")
            if self.repo_url:
                await f.write(f"Repository: {self.repo_url}\n")
            if self.branch:
                await f.write(f"Branch: {self.branch}\n")
            if self.subdir:
                await f.write(f"Subdir: {self.subdir.strip('/')}\n")

        # Package everything
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in self.output_files:
                arcname = file.relative_to(self.output_dir.parent)
                zipf.write(file, arcname)

            for asset_file, rel_path in copied_assets:
                arcname = Path("assets") / rel_path
                zipf.write(asset_file, arcname)

            zipf.write(readme_path, "README.txt")

        # Cleanup temp files
        shutil.rmtree(assets_dir, ignore_errors=True)
        readme_path.unlink(missing_ok=True)

        return zip_path
