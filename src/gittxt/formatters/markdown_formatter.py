from pathlib import Path
import aiofiles
from datetime import datetime, timezone
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.subcat_utils import detect_subcategory
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.formatter_utils import sort_textual_files


class MarkdownFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None, branch: str = None, subdir: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url
        self.branch = branch
        self.subdir = subdir

    async def generate(self, text_files, non_textual_files, summary_data: dict, mode="rich"):
        output_file = self.output_dir / f"{self.repo_name}.md"
        ordered_files = sort_textual_files(text_files)

        async with aiofiles.open(output_file, "w", encoding="utf-8") as md:
            # === Header Metadata ===
            await md.write(f"# 🧾 Gittxt Report for `{self.repo_name}`\n\n")
            await md.write(f"- **Generated**: `{datetime.now(timezone.utc).isoformat()} UTC`\n")
            if self.branch:
                await md.write(f"- **Branch**: `{self.branch}`\n")
            if self.subdir:
                await md.write(f"- **Subdir**: `{self.subdir.strip('/')}`\n")
            if self.repo_url:
                await md.write(f"- **Repository**: [{self.repo_url}]({self.repo_url})\n")
            await md.write(f"- **Format**: `markdown`\n\n")

            # === Directory Tree ===
            if mode == "rich":
                await md.write("## 📂 Directory Tree\n")
                await md.write("```text\n")
                await md.write(f"{self.tree_summary}\n")
                await md.write("```\n\n")

                # === Summary ===
                formatted = summary_data.get("formatted", {})
                await md.write("## 📊 Summary Report\n")
                await md.write(f"- **Total Files**: `{summary_data.get('total_files')}`\n")
                await md.write(f"- **Total Size**: `{formatted.get('total_size', summary_data.get('total_size'))}`\n")
                await md.write(f"- **Estimated Tokens**: `{formatted.get('estimated_tokens', summary_data.get('estimated_tokens'))}`\n\n")

                # === Breakdown Table ===
                breakdown = summary_data.get("file_type_breakdown", {})
                tokens_by_type = formatted.get("tokens_by_type", {})
                if breakdown:
                    await md.write("### File Type Breakdown\n\n")
                    await md.write("| Subcategory | File Count | Token Estimate |\n")
                    await md.write("|-------------|-------------|----------------|\n")
                    for subcat in sorted(breakdown):
                        count = breakdown[subcat]
                        tokens = tokens_by_type.get(subcat, summary_data.get("tokens_by_type", {}).get(subcat, 0))
                        await md.write(f"| {subcat} | {count} | {tokens} |\n")
                    await md.write("\n")

            # === Textual Files ===
            await md.write("## 📝 Extracted Textual Files\n")
            for file in ordered_files:
                rel = file.relative_to(self.repo_path)
                subcat = detect_subcategory(file, "TEXTUAL")
                file_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
                content = await async_read_text(file) or ""
                content = content if mode == "rich" else content[:300]
                size_bytes = file.stat().st_size
                tokens = summary_data.get("tokens_by_type", {}).get(subcat, 0)

                await md.write(f"\n### `{rel}` ({subcat})\n")
                if mode == "rich":
                    await md.write(f"- **Size**: `{size_bytes} bytes`\n")
                    await md.write(f"- **Tokens (est.)**: `{tokens}`\n")
                    if file_url:
                        await md.write(f"- **URL**: [{file_url}]({file_url})\n")
                await md.write("\n```text\n")
                await md.write(content.strip())
                await md.write("\n```\n")

            # === Non-Textual Assets ===
            if mode == "rich" and non_textual_files:
                await md.write("\n## 🎨 Non-Textual Assets\n")
                for asset in non_textual_files:
                    rel = asset.relative_to(self.repo_path)
                    subcat = detect_subcategory(asset, "NON-TEXTUAL")
                    asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
                    size_bytes = asset.stat().st_size
                    await md.write(f"- `{rel}` ({subcat}) | **Size**: `{size_bytes} bytes`")
                    if asset_url:
                        await md.write(f" | [URL]({asset_url})")
                    await md.write("\n")

        return output_file
