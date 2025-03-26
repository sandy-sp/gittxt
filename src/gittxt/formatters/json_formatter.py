# src/gittxt/formatters/json_formatter.py

from pathlib import Path
import json
import aiofiles
from datetime import datetime, timezone
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.formatter_utils import sort_textual_files
from gittxt.utils.subcat_utils import detect_subcategory

class JSONFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url

    async def generate(self, text_files, non_textual_files, mode="rich"):
        """
        Generate a JSON output with optional 'rich' mode (full summary, code blocks, etc.)
        or 'lite' mode (minimal content).
        """
        output_file = self.output_dir / f"{self.repo_name}.json"

        if mode == "rich":
            summary = await generate_summary(text_files + non_textual_files)
        else:
            # Minimal summary if 'lite'
            summary = {
                "total_files": len(text_files),
                "total_size": sum(f.stat().st_size for f in text_files + non_textual_files),
                "estimated_tokens": 0,
                "file_type_breakdown": {},
                "tokens_by_type": {}
            }

        ordered_files = sort_textual_files(text_files)

        data = {
            "repository_structure": self.tree_summary,
            "files": []
        }

        # In "rich" mode, add detailed metadata and assets
        if mode == "rich":
            data["metadata"] = {
                "repo_name": self.repo_name,
                "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
                "format": "json"
            }
            data["summary"] = summary
            data["assets"] = []

        # TEXTUAL section
        for file in ordered_files:
            rel = file.relative_to(self.repo_path)
            subcat = detect_subcategory(file, "TEXTUAL")  # second arg since we already know it's textual
            file_url = build_github_url(self.repo_url, rel) if self.repo_url else ""

            content = ""
            if mode == "rich":
                # read full content
                content = await async_read_text(file) or ""
            # in "lite" mode, you might skip content or only snippet the first X lines
            elif mode == "lite":
                # example: read a short snippet
                raw = await async_read_text(file) or ""
                content = raw[:200]  # snippet

            file_obj = {
                "file": str(rel),
                "content": content.strip() if content else ""
            }

            if mode == "rich":
                file_obj.update({
                    "type": subcat,
                    "size_bytes": file.stat().st_size,
                    "tokens_est": summary["tokens_by_type"].get(subcat, 0),
                    "url": file_url
                })

            data["files"].append(file_obj)

        # NON-TEXTUAL section
        if mode == "rich":
            for asset in non_textual_files:
                rel = asset.relative_to(self.repo_path)
                subcat = detect_subcategory(asset, "NON-TEXTUAL")
                asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
                data["assets"].append({
                    "file": str(rel),
                    "type": subcat,
                    "size_bytes": asset.stat().st_size,
                    "url": asset_url
                })

        async with aiofiles.open(output_file, "w", encoding="utf-8") as json_file:
            await json_file.write(json.dumps(data, indent=4, ensure_ascii=False))

        return output_file
