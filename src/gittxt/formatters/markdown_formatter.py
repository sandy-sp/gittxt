from pathlib import Path
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text
from datetime import datetime, timezone
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.formatter_utils import sort_textual_files
from gittxt.utils.subcat_utils import detect_subcategory
from gittxt.utils.formatter_utils import detect_language

class MarkdownFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url  # needed for asset URL generation

    async def generate(self, text_files, non_textual_files, mode="rich"):
        output_file = self.output_dir / f"{self.repo_name}.md"

        if mode == "rich":
            summary = await generate_summary(text_files + non_textual_files)
        else:
            summary = {"total_files": len(text_files), "total_size": 0, "estimated_tokens": 0, "tokens_by_type": {}}

        ordered_files = sort_textual_files(text_files)

        async with aiofiles.open(output_file, "w", encoding="utf-8") as md_file:
            if mode == "rich":
                await md_file.write(f"# 📦 Gittxt Report for `{self.repo_name}`\n")
                await md_file.write(f"- Generated: `{datetime.now(timezone.utc).isoformat()} UTC`\n")
                await md_file.write("- Format: `markdown`\n\n")

                await md_file.write("## 🗂 Directory Tree\n")
                await md_file.write(f"```\n{self.tree_summary}\n```\n\n")

                await md_file.write("## 📊 Summary Report\n")
                await md_file.write(f"- Total Files: `{summary['total_files']}`\n")
                await md_file.write(f"- Total Size: `{summary['total_size']} bytes`\n")
                await md_file.write(f"- Estimated Tokens: `{summary['estimated_tokens']}`\n\n")

                await md_file.write("## 📝 Extracted Textual Files\n")

            for file in ordered_files:
                rel = file.relative_to(self.repo_path.resolve())
                subcat = detect_subcategory(file)
                lang = detect_language(file)
                try:
                    content = await async_read_text(file)
                except UnicodeDecodeError as ude:
                    logger.warning(f"Unicode decode error in file {file}: {ude}. Skipping file.")
                    continue
                if not content:
                    continue
                token_est = summary.get("tokens_by_type", {}).get(subcat, 0)

                if mode == "rich":
                    await md_file.write(f"\n### 📄 `{rel}` ({subcat})\n")
                    await md_file.write(f"- Size: `{file.stat().st_size} bytes`\n")
                    await md_file.write(f"- Tokens (est.): `{token_est}`\n")
                    await md_file.write(f"```{lang}\n{content.strip()}\n```\n")
                else:
                    await md_file.write(f"\n### `{rel}`\n")
                    await md_file.write(f"```\n{content.strip()}\n```\n")

            if mode == "rich":
                await md_file.write("\n## 🎨 Non-Textual Assets\n")
                for asset in non_textual_files:
                    rel = asset.relative_to(self.repo_path.resolve())
                    subcat = detect_subcategory(asset)
                    asset_url = build_github_url(self.repo_url, rel) if self.repo_url and self.repo_url.startswith("http") else ""
                    await md_file.write(f"- `{rel}` ({subcat}) | Size: `{asset.stat().st_size} bytes` {asset_url}\n")

        return output_file


    def _detect_code_language(self, suffix: str) -> str:
        mapping = {
            ".py": "python", ".js": "javascript", ".ts": "typescript", ".sh": "bash", ".json": "json",
            ".md": "markdown", ".yml": "yaml", ".yaml": "yaml", ".html": "html", ".csv": "csv"
        }
        return mapping.get(suffix.lower(), "")
