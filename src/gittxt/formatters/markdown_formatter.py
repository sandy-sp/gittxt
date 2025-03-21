from pathlib import Path
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.filetype_utils import classify_file
from gittxt.utils.hash_utils import get_file_hash
from datetime import datetime, timezone

class MarkdownFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary

    async def generate(self, text_files, asset_files):
        output_file = self.output_dir / f"{self.repo_name}.md"
        summary = generate_summary(text_files + asset_files)
        
        async with aiofiles.open(output_file, "w", encoding="utf-8") as md_file:
            # Metadata Header
            await md_file.write(f"# 📦 Gittxt Report for `{self.repo_name}`\n")
            await md_file.write(f"- Generated: `{datetime.now(timezone.utc).isoformat()} UTC`\n")
            await md_file.write(f"- Format: `markdown`\n\n")

            # Directory Tree
            await md_file.write("## 🗂 Directory Tree\n")
            await md_file.write(f"```\n{self.tree_summary}\n```\n\n")

            # Summary Section
            await md_file.write("## 📊 Summary Report\n")
            await md_file.write(f"- Total Files: `{summary['total_files']}`\n")
            await md_file.write(f"- Total Size: `{summary['total_size']} bytes`\n")
            await md_file.write(f"- Estimated Tokens: `{summary['estimated_tokens']}`\n\n")
            await md_file.write("### Tokens by Type\n")
            for k, v in summary["tokens_by_type"].items():
                await md_file.write(f"- `{k}`: `{v}`\n")
            await md_file.write("\n### File Types Breakdown\n")
            for k, v in summary["file_type_breakdown"].items():
                await md_file.write(f"- `{k}`: `{v}`\n")
            await md_file.write("\n---\n\n")

            # File Sections
            for file in text_files:
                rel = Path(file).relative_to(self.repo_path)
                file_type = classify_file(file)
                sha256 = get_file_hash(file) or "N/A"
                content = await async_read_text(file)
                if content:
                    lang = self._detect_code_language(file.suffix)
                    await md_file.write(f"### 📄 `{rel}` ({file_type}) | `SHA256: {sha256}`\n\n")
                    await md_file.write(f"```{lang}\n{content.strip()}\n```\n\n")

        return output_file

    def _detect_code_language(self, suffix: str) -> str:
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".sh": "bash",
            ".json": "json",
            ".md": "markdown",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".txt": "",
            ".ipynb": "json",
        }
        return mapping.get(suffix.lower(), "")
