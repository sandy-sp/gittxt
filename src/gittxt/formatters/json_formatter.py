from pathlib import Path
import aiofiles
import json
from datetime import datetime, timezone
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.formatter_utils import sort_textual_files
from gittxt.utils.subcat_utils import detect_subcategory
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.summary_utils import (
    estimate_tokens_from_file,
    format_number_short,
    format_size_short
)


class JSONFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None, branch: str = None, subdir: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url
        self.branch = branch
        self.subdir = subdir

    async def generate(self, text_files, non_textual_files, summary_data: dict, mode="rich"):
        output_file = self.output_dir / f"{self.repo_name}.json"
        ordered_files = sort_textual_files(text_files)

        files_section = []
        for file in ordered_files:
            rel = file.relative_to(self.repo_path)
            subcat = detect_subcategory(file, "TEXTUAL")
            file_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
            raw_text = await async_read_text(file) or ""
            text = raw_text if mode == "rich" else raw_text[:300]

            size_bytes = file.stat().st_size
            token_count = await estimate_tokens_from_file(file)
            size_fmt = format_size_short(size_bytes)
            token_fmt = format_number_short(token_count)

            files_section.append({
                "path": str(rel),
                "subcategory": subcat,
                "size_bytes": size_bytes,
                "size_human": size_fmt,
                "tokens_estimate": token_count,
                "tokens_human": token_fmt,
                "content": text.strip(),
                "url": file_url
            })

        assets_section = []
        for asset in non_textual_files:
            rel = asset.relative_to(self.repo_path)
            subcat = detect_subcategory(asset, "NON-TEXTUAL")
            asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
            size_bytes = asset.stat().st_size
            size_fmt = format_size_short(size_bytes)

            assets_section.append({
                "path": str(rel),
                "subcategory": subcat,
                "size_bytes": size_bytes,
                "size_human": size_fmt,
                "url": asset_url
            })

        output = {
            "repository": {
                "name": self.repo_name,
                "url": self.repo_url,
                "branch": self.branch,
                "subdir": self.subdir,
                "tree_summary": self.tree_summary,
                "generated_at": datetime.now(timezone.utc).isoformat() + " UTC"
            },
            "summary": {
                "total_files": summary_data.get("total_files"),
                "total_size_bytes": summary_data.get("total_size"),
                "estimated_tokens": summary_data.get("estimated_tokens"),
                "formatted": summary_data.get("formatted"),
                "file_type_breakdown": summary_data.get("file_type_breakdown"),
                "tokens_by_type": summary_data.get("tokens_by_type"),
            },
            "files": files_section,
            "assets": assets_section
        }

        async with aiofiles.open(output_file, "w", encoding="utf-8") as jf:
            await jf.write(json.dumps(output, indent=2))

        return output_file
