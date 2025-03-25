from pathlib import Path
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.filetype_utils import classify_simple
from datetime import datetime, timezone
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.formatter_utils import sort_textual_files

class TextFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url

    async def generate(self, text_files, non_textual_files):
        output_file = self.output_dir / f"{self.repo_name}.txt"
        summary = await generate_summary(text_files + non_textual_files)

        ordered_files = sort_textual_files(text_files)

        async with aiofiles.open(output_file, "w", encoding="utf-8") as txt_file:
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
            for file in ordered_files:
                rel = file.relative_to(self.repo_path.resolve())
                primary, subcat = classify_simple(file)
                content = await async_read_text(file)
                if not content:
                    continue
                token_est = summary.get("tokens_by_type", {}).get(subcat, 0)
                await txt_file.write(f"\n---\nFILE: {rel} | TYPE: {subcat} | SIZE: {file.stat().st_size} bytes | TOKENS: {token_est}\n---\n")
                await txt_file.write(f"{content.strip()}\n")

            await txt_file.write("\n=== 🎨 Non-Textual Assets ===\n")
            for asset in non_textual_files:
                rel = asset.relative_to(self.repo_path.resolve())
                primary, subcat = classify_simple(asset)
                asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
                await txt_file.write(f"{rel} | TYPE: {subcat} | SIZE: {asset.stat().st_size} bytes {asset_url}\n")

        return output_file
