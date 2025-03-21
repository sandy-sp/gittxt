from pathlib import Path
import json
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.filetype_utils import classify_file
from gittxt.utils.file_utils import async_read_text
from datetime import datetime, timezone

class JSONFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary

    async def generate(self, text_files, asset_files):
        output_file = self.output_dir / f"{self.repo_name}.json"
        summary = generate_summary(text_files + asset_files)

        data = {
            "metadata": {
                "repo_name": self.repo_name,
                "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
                "format": "json"
            },
            "repository_structure": self.tree_summary,
            "summary": summary,
            "files": []
        }

        for file in text_files:
            rel = Path(file).relative_to(self.repo_path)
            file_type = classify_file(file)
            content = await async_read_text(file)
            if content:
                data["files"].append({
                    "file": str(rel),
                    "file_type": file_type,
                    "content": content.strip()
                })

        async with aiofiles.open(output_file, "w", encoding="utf-8") as json_file:
            await json_file.write(json.dumps(data, indent=4, ensure_ascii=False))

        return output_file
