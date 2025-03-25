from pathlib import Path
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.filetype_utils import classify_simple
from datetime import datetime, timezone
from gittxt.utils.github_url_utils import build_github_url
from gittxt.utils.formatter_utils import sort_textual_files

class MarkdownFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url  # needed for asset URL generation

    async def generate(self, text_files, non_textual_files):
        output_file = self.output_dir / f"{self.repo_name}.md"
        summary = generate_summary(text_files + non_textual_files)

        # Sort TEXTUAL files by priority order
        ordered_files = sort_textual_files(text_files)

        async with aiofiles.open(output_file, "w", encoding="utf-8") as md_file:
            await md_file.write(f"# 📦 Gittxt Report for `{self.repo_name}`\n")
            await md_file.write(f"- Generated: `{datetime.now(timezone.utc).isoformat()} UTC`\n")
            await md_file.write("- Format: `markdown`\n\n")

            await md_file.write("## 🗂 Directory Tree\n")
            await md_file.write(f"```\n{self.tree_summary}\n```\n\n")

            await md_file.write("## 📊 Summary Report\n")
            await md_file.write(f"- Total Files: `{summary['total_files']}`\n")
            await md_file.write(f"- Total Size: `{summary['total_size']} bytes`\n")
            await md_file.write(f"- Estimated Tokens: `{summary['estimated_tokens']}`\n\n")

            # TEXTUAL FILES SECTION
            await md_file.write("## 📝 Extracted Textual Files\n")
            for file in ordered_files:
                rel = Path(file).relative_to(self.repo_path)
                primary, subcat = classify_simple(file)
                lang = self._detect_code_language(file.suffix)
                content = await async_read_text(file)
                if not content:
                    continue
                token_est = summary.get("tokens_by_type", {}).get(subcat, 0)
                await md_file.write(f"\n### 📄 `{rel}` ({subcat})\n")
                await md_file.write(f"- Size: `{file.stat().st_size} bytes`\n")
                await md_file.write(f"- Tokens (est.): `{token_est}`\n")
                await md_file.write(f"```{lang}\n{content.strip()}\n```\n")

            # NON-TEXTUAL FILES SECTION
            await md_file.write("\n## 🎨 Non-Textual Assets\n")
            for asset in non_textual_files:
                rel = Path(asset).relative_to(self.repo_path)
                primary, subcat = classify_simple(asset)
                asset_url = build_github_url(self.repo_url, rel) if self.repo_url else ""
                await md_file.write(f"- `{rel}` ({subcat}) | Size: `{asset.stat().st_size} bytes` {asset_url}\n")

        return output_file

    def _detect_code_language(self, suffix: str) -> str:
        mapping = {
            ".py": "python", ".js": "javascript", ".ts": "typescript", ".sh": "bash", ".json": "json",
            ".md": "markdown", ".yml": "yaml", ".yaml": "yaml", ".html": "html", ".csv": "csv"
        }
        return mapping.get(suffix.lower(), "")
