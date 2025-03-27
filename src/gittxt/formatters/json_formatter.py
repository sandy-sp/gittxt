from pathlib import Path
import aiofiles
import json
from datetime import datetime, timezone
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.formatter_utils import sort_textual_files
from gittxt.utils.subcat_utils import detect_subcategory
from gittxt.utils.file_utils import async_read_text


class JSONFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None, branch: str = None, subdir: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url
        self.branch = branch
        self.subdir = subdir

    async def generate(self, text_files, non_textual_files, summary_data: dict, mode: str = "rich"):
        output_file = self.output_dir / f"{self.repo_name}.json"
        ordered_files = sort_textual_files(text_files)

        output_data = {
            "repository": {
                "name": self.repo_name,
                "branch": self.branch,
                "subdir": self.subdir.strip("/") if self.subdir else None,
                "repo_url": self.repo_url,
                "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
                "format": "json"
            },
            "directory_tree": self.tree_summary,
            "summary": summary_data,
            "formatted": summary_data["formatted"],
            "files": [],
            "assets": []
        }

        # TEXTUAL FILES
        for file in ordered_files:
            rel = file.relative_to(self.repo_path)
            subcat = detect_subcategory(file, "TEXTUAL")
            file_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
            raw = await async_read_text(file) or ""
            content = raw if mode == "rich" else raw[:300]

            file_obj = {
                "path": str(rel),
                "type": subcat,
                "size_bytes": file.stat().st_size,
                "url": file_url,
                "tokens_est": summary_data.get("tokens_by_type", {}).get(subcat, 0),
                "content": content.strip()
            }
            output_data["files"].append(file_obj)

        # NON-TEXTUAL FILES
        for asset in non_textual_files:
            rel = asset.relative_to(self.repo_path)
            subcat = detect_subcategory(asset, "NON-TEXTUAL")
            asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""

            asset_obj = {
                "path": str(rel),
                "type": subcat,
                "size_bytes": asset.stat().st_size,
                "url": asset_url
            }
            output_data["assets"].append(asset_obj)

        # Write to file
        async with aiofiles.open(output_file, "w", encoding="utf-8") as json_file:
            await json_file.write(json.dumps(output_data, indent=4, ensure_ascii=False))

        return output_file
