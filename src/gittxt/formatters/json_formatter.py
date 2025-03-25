from pathlib import Path
import json
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.filetype_utils import classify_simple
from gittxt.utils.file_utils import async_read_text
from datetime import datetime, timezone
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.formatter_utils import sort_textual_files

class JSONFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url

    async def generate(self, text_files, non_textual_files):
        output_file = self.output_dir / f"{self.repo_name}.json"
        summary = await generate_summary(text_files + non_textual_files)

        ordered_files = sort_textual_files(text_files)

        data = {
            "metadata": {
                "repo_name": self.repo_name,
                "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
                "format": "json"
            },
            "repository_structure": self.tree_summary,
            "summary": summary,
            "files": [],
            "assets": []
        }

        # TEXTUAL FILES SECTION
        for file in ordered_files:
            rel = file.relative_to(self.repo_path.resolve())
            primary, subcat = classify_simple(file)
            content = await async_read_text(file)
            if not content:
                continue
            token_est = summary.get("tokens_by_type", {}).get(subcat, 0)
            file_url = build_github_url(self.repo_url, rel)
            data["files"].append({
                "file": str(rel),
                "type": subcat,
                "size_bytes": file.stat().st_size,
                "tokens_est": token_est,
                "content": content.strip(),
                "url": file_url
            })

        # NON-TEXTUAL FILES SECTION
        for asset in non_textual_files:
            rel = asset.relative_to(self.repo_path.resolve())
            primary, subcat = classify_simple(asset)
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
