from pathlib import Path
import aiofiles
from datetime import datetime, timezone
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.formatter_utils import sort_textual_files
from gittxt.utils.subcat_utils import detect_subcategory

class TextFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url

    async def generate(self, text_files, non_textual_files, mode="rich"):
        """
        A plain text report with optional 'rich' details or 'lite' brevity.
        """
        output_file = self.output_dir / f"{self.repo_name}.txt"

        if mode == "rich":
            summary = await generate_summary(text_files + non_textual_files)
        else:
            summary = {
                "total_files": len(text_files),
                "total_size": sum(f.stat().st_size for f in text_files + non_textual_files),
                "estimated_tokens": 0,
                "file_type_breakdown": {},
                "tokens_by_type": {}
            }

        ordered_files = sort_textual_files(text_files)

        async with aiofiles.open(output_file, "w", encoding="utf-8") as txt_file:
            if mode == "rich":
                await txt_file.write("=== Gittxt Report ===\n")
                await txt_file.write(f"Repo: {self.repo_name}\n")
                await txt_file.write(f"Generated: {datetime.now(timezone.utc).isoformat()} UTC\n\n")

                await txt_file.write("=== Directory Tree ===\n")
                await txt_file.write(f"{self.tree_summary}\n\n")

                await txt_file.write("=== 📊 Summary Report ===\n")
                await txt_file.write(f"Total Files: {summary['total_files']}\n")
                await txt_file.write(f"Total Size: {summary['total_size']} bytes\n")
                await txt_file.write(f"Estimated Tokens: {summary['estimated_tokens']}\n\n")

                await txt_file.write("=== 📝 Extracted Textual Files ===\n")
            else:
                await txt_file.write(f"Gittxt Lite Report - {self.repo_name}\n\n")

            # TEXTUAL FILES
            for file in ordered_files:
                rel = file.relative_to(self.repo_path)
                subcat = detect_subcategory(file, "TEXTUAL")
                asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""

                content = ""
                if mode == "rich":
                    content = await async_read_text(file) or ""
                else:
                    raw = await async_read_text(file) or ""
                    content = raw[:300]

                if mode == "rich":
                    await txt_file.write(f"\n---\nFILE: {rel} | TYPE: {subcat} | SIZE: {file.stat().st_size} bytes | TOKENS: {summary['tokens_by_type'].get(subcat, 0)}\n---\n")
                else:
                    await txt_file.write(f"\n--- {rel} ---\n")

                await txt_file.write(f"{content.strip()}\n")

            # NON-TEXTUAL FILES
            if mode == "rich":
                await txt_file.write("\n=== 🎨 Non-Textual Assets ===\n")
                for asset in non_textual_files:
                    rel = asset.relative_to(self.repo_path)
                    subcat = detect_subcategory(asset, "NON-TEXTUAL")
                    asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
                    await txt_file.write(f"{rel} | TYPE: {subcat} | SIZE: {asset.stat().st_size} bytes {asset_url}\n")

        return output_file
