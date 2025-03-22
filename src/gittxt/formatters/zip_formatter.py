from pathlib import Path
from zipfile import ZipFile
import asyncio

class ZipFormatter:
    def __init__(self, repo_name: str, output_dir: Path, output_files: list, non_textual_files: list):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.output_files = output_files  # txt, json, md outputs
        self.non_textual_files = non_textual_files

    async def generate(self) -> Path:
        zip_path = self.output_dir / f"{self.repo_name}_bundle.zip"
        await asyncio.to_thread(self._create_zip, zip_path)
        return zip_path

    def _create_zip(self, zip_dest: Path):
        zip_dest.parent.mkdir(parents=True, exist_ok=True)

        with ZipFile(zip_dest, "w") as zipf:
            # Include all formatted TEXTUAL outputs at ZIP root
            for output in self.output_files:
                zipf.write(output, arcname=output.name)

            # Include NON-TEXTUAL files inside /assets/
            for asset in self.non_textual_files:
                arcname = f"assets/{asset.name}"
                zipf.write(asset, arcname=arcname)

        if zip_dest.exists():
            print(f"✅ ZIP created at {zip_dest}")
        else:
            print(f"❌ Failed to create ZIP at {zip_dest}")
