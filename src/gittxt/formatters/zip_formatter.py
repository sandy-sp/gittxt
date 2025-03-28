import zipfile
import tempfile
import shutil
import json
from pathlib import Path
from datetime import datetime, timezone
from gittxt.utils.summary_utils import format_size_short, format_number_short


class ZipFormatter:
    def __init__(self, repo_name, output_dir: Path, output_files, non_textual_files, repo_path: Path, repo_url: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.output_files = output_files
        self.non_textual_files = non_textual_files
        self.repo_path = repo_path
        self.repo_url = repo_url

    async def generate(self):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        zip_path = self.output_dir / f"{self.repo_name}-{timestamp}.zip"

        with tempfile.TemporaryDirectory() as tempdir:
            tempdir = Path(tempdir)

            # === Copy Outputs ===
            outputs_dir = tempdir / "outputs"
            outputs_dir.mkdir(parents=True, exist_ok=True)

            for file in self.output_files:
                if file.exists():
                    shutil.copy(file, outputs_dir / file.name)

            # === Copy Assets ===
            if self.non_textual_files:
                assets_dir = tempdir / "assets"
                assets_dir.mkdir(parents=True, exist_ok=True)
                for asset in self.non_textual_files:
                    rel = asset.relative_to(self.repo_path)
                    target = assets_dir / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(asset, target)

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
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in tempdir.rglob("*"):
                    zf.write(file, file.relative_to(tempdir))

        return zip_path

    async def _write_summary_json(self, path: Path):
        # Minimal fallback summary — this can be extended to pull from actual summary_data
        summary_data = {
            "repo": self.repo_name,
            "url": self.repo_url,
            "generated_at": datetime.now(timezone.utc).isoformat() + " UTC",
            "files": [f.name for f in self.output_files],
            "non_textual_assets": [str(f.relative_to(self.repo_path)) for f in self.non_textual_files]
        }
        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(summary_data, indent=2))

    async def _write_manifest_json(self, path: Path):
        entries = []

        for f in self.output_files:
            entries.append({
                "type": "output",
                "name": f.name,
                "size_bytes": f.stat().st_size,
                "size_human": format_size_short(f.stat().st_size)
            })

        for f in self.non_textual_files:
            rel = f.relative_to(self.repo_path)
            entries.append({
                "type": "asset",
                "path": str(rel),
                "size_bytes": f.stat().st_size,
                "size_human": format_size_short(f.stat().st_size)
            })

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

        async with aiofiles.open(path, "w", encoding="utf-8") as f:
            await f.write("\n".join(lines))
