from pathlib import Path
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text

class MarkdownFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary

    async def generate(self, text_files, asset_files):
        output_file = self.output_dir / f"{self.repo_name}.md"
        async with aiofiles.open(output_file, "w", encoding="utf-8") as out:
            await out.write(f"# 📂 Repository Overview: `{self.repo_name}`\n\n")
            await out.write(f"## 📜 Folder Structure\n```\n{self.tree_summary}\n```\n")

            summary = generate_summary(text_files + asset_files)
            summary_md = "\n".join([f"- **{k}**: {v}" for k, v in summary.items()])
            await out.write(f"\n## 📊 Summary Report\n\n{summary_md}\n")

            await out.write("\n## 📄 Extracted Files\n")
            for file in text_files:
                rel = Path(file).relative_to(self.repo_path)
                content = await async_read_text(file)
                if content:
                    lang = self._detect_code_language(rel.suffix)
                    await out.write(f"\n### `{rel}`\n```{lang}\n{content.strip()}\n```\n")

            if asset_files:
                await out.write("\n## 📦 Asset Files\n")
                for asset in asset_files:
                    rel = Path(asset).relative_to(self.repo_path)
                    ext = rel.suffix.lower()
                    if ext in [".png", ".jpg", ".jpeg", ".gif", ".svg"]:
                        await out.write(f"![{rel}]({rel})\n")
                    else:
                        await out.write(f"- [{rel}]({rel})\n")
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
            ".txt": "plaintext",
            ".ipynb": "json",
        }
        return mapping.get(suffix.lower(), "plaintext")
