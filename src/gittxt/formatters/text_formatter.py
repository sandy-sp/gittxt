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
    format_size_short,
)


class TextFormatter:
    def __init__(
        self,
        repo_name,
        output_dir: Path,
        repo_path: Path,
        tree_summary: str,
        repo_url: str = None,
        branch: str = None,
        subdir: str = None,
        mode: str = "rich",
    ):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = Path(repo_path).resolve()
        self.repo_root = self.repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url
        self.branch = branch
        self.subdir = subdir
        self.mode = mode

    async def generate(
        self, text_files, non_textual_files, summary_data: dict
    ):
        mode = self.mode
        output_file = self.output_dir / f"{self.repo_name}.txt"
        ordered_files = sort_textual_files(text_files, base_path=self.repo_root)

        async with aiofiles.open(output_file, "w", encoding="utf-8") as txt_file:
            if mode == "lite":
                await txt_file.write(f"Repo: {self.repo_name}\n")
                if self.repo_url:
                    owner = self.repo_url.rstrip("/").split("/")[-2]
                    await txt_file.write(f"Owner: {owner}\n")
                if self.branch:
                    await txt_file.write(f"Branch: {self.branch}\n")
                if self.subdir:
                    await txt_file.write(f"Subdir: {self.subdir.strip('/')}\n")
                await txt_file.write("\n=== Directory Tree ===\n")
                await txt_file.write(f"{self.tree_summary}\n\n")
                await txt_file.write("=== Textual Files ===\n")

                for text_file in ordered_files:
                    rel_path = text_file.resolve().relative_to(self.repo_root)
                    raw = await async_read_text(text_file) or "[no content]"
                    await txt_file.write(f"--- File: {rel_path} ---\n")
                    await txt_file.write(f"{raw.strip()}\n\n")
                return output_file
            
            else:
                # === Rich Mode ===
                await txt_file.write("=== Gittxt Report ===\n")
                await txt_file.write(f"Repo: {self.repo_name}\n")
                await txt_file.write(
                    f"Generated: {datetime.now(timezone.utc).isoformat()} UTC\n"
                )
                if self.branch:
                    await txt_file.write(f"Branch: {self.branch}\n")
                if self.subdir:
                    await txt_file.write(f"Subdir: {self.subdir.strip('/')}\n")
                await txt_file.write("\n=== Directory Tree ===\n")
                await txt_file.write(f"{self.tree_summary}\n\n")

                formatted = summary_data.get("formatted", {})
                await txt_file.write("=== 📊 Summary Report ===\n")
                await txt_file.write(f"Total Files: {summary_data.get('total_files')}\n")
                await txt_file.write(f"Total Size: {formatted.get('total_size')}\n")
                await txt_file.write(
                    f"Estimated Tokens: {formatted.get('estimated_tokens')}\n\n"
                )

                await txt_file.write("=== 📝 Extracted Textual Files ===\n")
                for text_file in ordered_files:
                    rel_path = text_file.resolve().relative_to(self.repo_root)
                    subcat = detect_subcategory(text_file, "TEXTUAL")
                    asset_url = build_github_url(
                        self.repo_url, rel_path, self.branch, self.subdir
                    )
                    raw = await async_read_text(text_file) or "[no content]"
                    size_fmt = format_size_short(text_file.stat().st_size)
                    tokens_fmt = format_number_short(
                        await estimate_tokens_from_file(text_file)
                    )

                    await txt_file.write(
                        f"\n---\nFILE: {rel_path} | TYPE: {subcat} | SIZE: {size_fmt} | TOKENS: {tokens_fmt}\n---\n"
                    )
                    await txt_file.write(f"{raw.strip()}\n")

                if non_textual_files:
                    await txt_file.write("\n=== 🎨 Non-Textual Assets ===\n")
                    for asset in non_textual_files:
                        rel_path = asset.resolve().relative_to(self.repo_root)
                        subcat = detect_subcategory(asset, "NON-TEXTUAL")
                        asset_url = build_github_url(
                            self.repo_url, rel_path, self.branch, self.subdir
                        )
                        size_fmt = format_size_short(asset.stat().st_size)
                        await txt_file.write(
                            f"{rel_path} | TYPE: {subcat} | SIZE: {size_fmt}"
                        )
                        if asset_url:
                            await txt_file.write(f" | {asset_url}")
                        await txt_file.write("\n")

            return output_file