from pathlib import Path
import aiofiles
from datetime import datetime, timezone
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.formatter_utils import sort_textual_files
from gittxt.utils.subcat_utils import detect_subcategory
from gittxt.utils.summary_utils import (
    estimate_tokens_from_file,
    format_number_short,
    format_size_short
)


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
            if mode == "lite":
                # === LITE MODE HEADER ===
                # === HEADER ===
                await txt_file.write(f"Repo: {self.repo_name}\n")
                if self.repo_url:
                    owner = self.repo_url.rstrip("/").split("/")[-2]
                    await txt_file.write(f"Owner: {owner}\n")
                if self.branch:
                    await txt_file.write(f"Branch: {self.branch}\n")
                if self.subdir:
                    await txt_file.write(f"Subdir: {self.subdir.strip('/')}\n")
                await txt_file.write("\n")
                # === DIRECTORY TREE ===
                await txt_file.write("=== Directory Tree ===\n")
                await txt_file.write(f"{self.tree_summary}\n\n")
                # === TEXTUAL FILES SECTION ===
                await txt_file.write("=== Textual Files ===\n")
                for file in ordered_files:
                    rel = file.relative_to(self.repo_path)
                    raw = await async_read_text(file) or ""
                    await txt_file.write(f"--- File: {rel} ---\n")
                    await txt_file.write(f"{raw.strip()}\n\n")
                return output_file

            # === RICH MODE ===
            await txt_file.write("=== Gittxt Report ===\n")
            await txt_file.write(f"Repo: {self.repo_name}\n")
            await txt_file.write(f"Generated: {datetime.now(timezone.utc).isoformat()} UTC\n")
            if self.branch:
                await txt_file.write(f"Branch: {self.branch}\n")
            if self.subdir:
                await txt_file.write(f"Subdir: {self.subdir.strip('/')}\n")
            await txt_file.write("\n")

            await txt_file.write("=== Directory Tree ===\n")
            await txt_file.write(f"{self.tree_summary}\n\n")

            formatted = summary_data.get("formatted", {})
            await txt_file.write("=== 📊 Summary Report ===\n")
            await txt_file.write(f"Total Files: {summary_data.get('total_files')}\n")
            await txt_file.write(f"Total Size: {formatted.get('total_size')}\n")
            await txt_file.write(f"Estimated Tokens: {formatted.get('estimated_tokens')}\n\n")

            await txt_file.write("=== 📝 Extracted Textual Files ===\n")
            for file in ordered_files:
                rel = file.relative_to(self.repo_path)
                subcat = detect_subcategory(file, "TEXTUAL")
                asset_url = build_github_url(self.repo_url, rel, self.branch, self.subdir) if self.repo_url else ""
                raw = await async_read_text(file) or ""
                size_bytes = file.stat().st_size
                token_count = await estimate_tokens_from_file(file)
                size_fmt = format_size_short(size_bytes)
                tokens_fmt = format_number_short(token_count)

                await txt_file.write(f"\n---\nFILE: {rel} | TYPE: {subcat} | SIZE: {size_fmt} | TOKENS: {tokens_fmt}\n---\n")
                await txt_file.write(f"{raw.strip()}\n")

            if non_textual_files:
                await txt_file.write("\n=== 🎨 Non-Textual Assets ===\n")
                for asset in non_textual_files:
                    rel = asset.relative_to(self.repo_path)
                    subcat = detect_subcategory(asset, "NON-TEXTUAL")
                    asset_url = build_github_url(self.repo_url, rel, self.branch, self.subdir) if self.repo_url else ""
                    size_fmt = format_size_short(asset.stat().st_size)
                    await txt_file.write(f"{rel} | TYPE: {subcat} | SIZE: {size_fmt}")
                    if asset_url:
                        await txt_file.write(f" | {asset_url}")
                    await txt_file.write("\n")

        return output_file
