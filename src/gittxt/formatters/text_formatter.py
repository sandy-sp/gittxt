from pathlib import Path
import aiofiles
from datetime import datetime, timezone
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.formatter_utils import sort_textual_files
from gittxt.utils.subcat_utils import detect_subcategory


class TextFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None, branch: str = None, subdir: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url
        self.branch = branch
        self.subdir = subdir

    async def generate(self, text_files, non_textual_files, summary_data: dict, mode="rich"):
        output_file = self.output_dir / f"{self.repo_name}.txt"
        ordered_files = sort_textual_files(text_files)

        async with aiofiles.open(output_file, "w", encoding="utf-8") as txt_file:
            # === HEADER ===
            if mode == "rich":
                await txt_file.write("=== Gittxt Report ===\n")
                await txt_file.write(f"Repo: {self.repo_name}\n")
                await txt_file.write(f"Generated: {datetime.now(timezone.utc).isoformat()} UTC\n")
                if self.branch:
                    await txt_file.write(f"Branch: {self.branch}\n")
                if self.subdir:
                    await txt_file.write(f"Subdir: {self.subdir.strip('/')}\n")
                await txt_file.write("\n")

                # === TREE ===
                await txt_file.write("=== Directory Tree ===\n")
                await txt_file.write(f"{self.tree_summary}\n\n")

                # === SUMMARY ===
                formatted = summary_data.get("formatted", {})
                await txt_file.write("=== 📊 Summary Report ===\n")
                await txt_file.write(f"Total Files: {summary_data.get('total_files')}\n")
                await txt_file.write(f"Total Size: {formatted.get('total_size', summary_data.get('total_size'))}\n")
                await txt_file.write(f"Estimated Tokens: {formatted.get('estimated_tokens', summary_data.get('estimated_tokens'))}\n\n")
                await txt_file.write("=== 📝 Extracted Textual Files ===\n")
            else:
                await txt_file.write(f"Gittxt Lite Report - {self.repo_name}\n\n")

            # === TEXTUAL FILES ===
            for file in ordered_files:
                rel = file.relative_to(self.repo_path)
                subcat = detect_subcategory(file, "TEXTUAL")
                asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
                raw = await async_read_text(file) or ""
                content = raw if mode == "rich" else raw[:300]
                size_bytes = file.stat().st_size
                tokens = summary_data.get("tokens_by_type", {}).get(subcat, 0)

                if mode == "rich":
                    await txt_file.write(f"\n---\nFILE: {rel} | TYPE: {subcat} | SIZE: {size_bytes} bytes | TOKENS: {tokens}\n---\n")
                else:
                    await txt_file.write(f"\n--- {rel} ---\n")

                await txt_file.write(f"{content.strip()}\n")

            # === NON-TEXTUAL FILES ===
            if mode == "rich" and non_textual_files:
                await txt_file.write("\n=== 🎨 Non-Textual Assets ===\n")
                for asset in non_textual_files:
                    rel = asset.relative_to(self.repo_path)
                    subcat = detect_subcategory(asset, "NON-TEXTUAL")
                    asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
                    size_bytes = asset.stat().st_size
                    await txt_file.write(f"{rel} | TYPE: {subcat} | SIZE: {size_bytes} bytes")
                    if asset_url:
                        await txt_file.write(f" | {asset_url}")
                    await txt_file.write("\n")

        return output_file
