import aiofiles
import zipfile
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timezone
from core.utils.summary_utils import format_size_short
from core.core.logger import Logger

logger = Logger.get_logger(__name__)


class ZipFormatter:
    def __init__(
        self,
        repo_name,
        output_dir: Path,
        output_files,
        non_textual_files,
        repo_path: Path,
        repo_url: str = None,
    ):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.output_files = output_files
        self.non_textual_files = non_textual_files
        self.repo_path = Path(repo_path).resolve()
        self.repo_url = repo_url
        self.flatten_zip = False

    async def generate(self):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        zip_path = self.output_dir / f"{self.repo_name}-{timestamp}.zip"
        logger.info(f"📦 Zipped bundle created: {zip_path}")

        with tempfile.TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)

            # === Copy Outputs ===
            outputs_dir = tempdir / "outputs"
            outputs_dir.mkdir(parents=True, exist_ok=True)

            for f in self.output_files:
                if f.exists():
                    try:
                        arcname = (
                            f.relative_to(self.output_dir)
                            if not self.flatten_zip
                            else f.name
                        )
                    except ValueError:
                        arcname = f.name
                    target = outputs_dir / arcname
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(f, target)

            # === Copy Assets (Non-Textual Files) ===
            if self.non_textual_files:
                assets_dir = tempdir / "assets"
                assets_dir.mkdir(parents=True, exist_ok=True)
                for asset in self.non_textual_files:
                    if not asset.is_file():  # ✅ skip directories
                        logger.warning(f"⚠️ Skipped non-file asset: {asset}")
                        continue
                    try:
                        try:
                            rel = asset.resolve().relative_to(self.repo_path)
                        except ValueError:
                            rel = Path("unknown") / asset.name
                        target = assets_dir / rel
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy(asset, target)
                        logger.info(f"✅ Included asset: {asset} → {target}")
                    except ValueError:
                        rel = Path("unknown") / asset.name
                        logger.warning(f"⚠️ Asset outside repo path: {asset}")
                    except Exception as e:
                        print(f"⚠️ Failed to include asset: {asset} ({e})")

            # === Add Summary JSON ===
            summary_path = tempdir / "summary.json"
            await self._write_summary_json(summary_path)

            # === Add Manifest JSON ===
            manifest_path = tempdir / "manifest.json"
            await self._write_manifest_json(manifest_path)

            # === Add README.md ===
            readme_path = tempdir / "README.md"
            await self._write_readme(readme_path)

            # === Create ZIP ===
            try:
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for file in sorted(tempdir.rglob("*")):
                        if file.is_file():
                            try:
                                zf.write(file, file.relative_to(tempdir))
                            except Exception as e:
                                print(f"⚠️ Failed to add {file} to ZIP: {e}")
            except Exception as e:
                raise RuntimeError(f"❌ ZIP creation failed: {e}")

        # Confirm ZIP exists
        if not zip_path.exists():
            raise RuntimeError(f"❌ ZIP bundle creation failed: {zip_path} not found")

        return zip_path

    async def _write_summary_json(self, path: Path):
        summary_data = {
            "repo": self.repo_name,
            "url": self.repo_url,
            "generated_at": datetime.now(timezone.utc).isoformat() + " UTC",
            "files": [
                (
                    str(f.relative_to(self.output_dir))
                    if self.output_dir in f.parents
                    else str(f.name)
                )
                for f in self.output_files
            ],
            "non_textual_assets": [
                str(f.resolve().relative_to(self.repo_path))
                for f in self.non_textual_files
            ],
        }
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(summary_data, indent=2))

    async def _write_manifest_json(self, path: Path):
        entries = []

        for f in self.output_files:
            if f.exists():
                size = f.stat().st_size
                entries.append(
                    {
                        "type": "output",
                        "name": f.name,
                        "size_bytes": size,
                        "size_human": format_size_short(size),
                    }
                )

        for f in self.non_textual_files:
            if f.exists():
                try:
                    rel = f.resolve().relative_to(self.repo_path)
                    size = f.stat().st_size
                    entries.append(
                        {
                            "type": "asset",
                            "path": str(rel),
                            "size_bytes": size,
                            "size_human": format_size_short(size),
                        }
                    )
                except Exception:
                    pass

        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(entries, indent=2))

    async def _write_readme(self, path: Path):
        lines = [
            f"# 🧾 Gittxt ZIP Bundle for `{self.repo_name}`\n",
            f"- Generated at: `{datetime.now(timezone.utc).isoformat()} UTC`",
        ]
        if self.repo_url:
            lines.append(f"- Repository: [{self.repo_url}]({self.repo_url})")

        lines += [
            "\n## 📁 Structure",
            "- `outputs/`: Main output files (`.txt`, `.md`, `.json`)",
            "- `assets/`: Non-textual files (images, data, binaries)",
            "- `summary.json`: Basic metadata about this bundle",
            "- `manifest.json`: Full list of included files and sizes",
            "- `README.md`: This file",
        ]
        lines.append("\nExported with ❤️ by Gittxt.")
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write("\n".join(lines))
