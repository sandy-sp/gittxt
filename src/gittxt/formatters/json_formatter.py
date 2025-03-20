from pathlib import Path
import json
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.filetype_utils import classify_file

class JSONFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary

    async def read_file_content(self, file_path: Path):
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return await f.read()
        except Exception:
            return None

    async def generate(self, text_files, _):
        output_file = self.output_dir / f"{self.repo_name}.json"
        data = {
            "repository_structure": self.tree_summary,
            "summary": generate_summary(text_files),
            "files": [],
        }
        for file in text_files:
            rel = Path(file).relative_to(self.repo_path)
            content = await self.read_file_content(file)
            if content:
                data["files"].append({
                    "file": str(rel),
                    "content": content.strip(),
                    "file_type": classify_file(file)
                })
        async with aiofiles.open(output_file, "w", encoding="utf-8") as json_file:
            await json_file.write(json.dumps(data, indent=4))
        return output_file
