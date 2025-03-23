from pathlib import Path
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.filetype_utils import classify_simple
from datetime import datetime, timezone
from urllib.parse import urlparse
import re

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
        ordered_files = self._sort_textual_files(text_files)

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
                content = await async_read_text(file)
                token_est = summary.get("tokens_by_type", {}).get(subcat, 0)
                lang = self._detect_code_language(file.suffix)
                if content:
                    await md_file.write(f"\n### 📄 `{rel}` ({subcat})\n")
                    await md_file.write(f"- Size: `{file.stat().st_size} bytes`\n")
                    await md_file.write(f"- Tokens (est.): `{token_est}`\n")
                    await md_file.write(f"```{lang}\n{content.strip()}\n```\n")

            # NON-TEXTUAL FILES SECTION
            await md_file.write("\n## 🎨 Non-Textual Assets\n")
            for asset in non_textual_files:
                rel = Path(asset).relative_to(self.repo_path)
                primary, subcat = classify_simple(asset)
                asset_url = self._build_github_url(rel) if self.repo_url else ""
                await md_file.write(f"- `{rel}` ({subcat}) | Size: `{asset.stat().st_size} bytes` {asset_url}\n")

        return output_file

    def _sort_textual_files(self, files):
        priority = ["readme", "license", ".gitignore", "config", "docs", "code", "data"]
        def file_priority(file):
            fname = file.name.lower()
            if fname.startswith("readme"):
                return 0
            if fname in {"license", "notice"}:
                return 1
            if fname in {".gitignore", ".dockerignore", ".gitattributes"}:
                return 2
            ext_priority = {"configs": 3, "docs": 4, "code": 5, "data": 6}
            _, subcat = classify_simple(file)
            return ext_priority.get(subcat, 7)
        return sorted(files, key=file_priority)

    def _detect_code_language(self, suffix: str) -> str:
        mapping = {
            ".py": "python", ".js": "javascript", ".ts": "typescript", ".sh": "bash", ".json": "json",
            ".md": "markdown", ".yml": "yaml", ".yaml": "yaml", ".html": "html", ".csv": "csv"
        }
        return mapping.get(suffix.lower(), "")

    def _build_github_url(self, rel_path: Path) -> str:
        if not self.repo_url:
            return ""

        # Normalize and parse URL (support both https://github.com and git@github.com)
        repo_url = self.repo_url.replace("git@github.com:", "https://github.com/")
        repo_url = repo_url.replace(".git", "")
        parsed = urlparse(repo_url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            return ""  # Invalid URL fallback

        owner, repo = path_parts[:2]
        subdir = "/".join(path_parts[3:]) if "tree" in path_parts else ""
        branch = "main"
        
        # Extract branch if URL contains /tree/<branch>/
        tree_match = re.search(r"/tree/([^/]+)", parsed.path)
        if tree_match:
            branch = tree_match.group(1)

        rel_posix = rel_path.as_posix()
        
        # Construct clean GitHub URL
        base_url = f"https://github.com/{owner}/{repo}/blob/{branch}"
        if subdir:
            return f"{base_url}/{subdir}/{rel_posix}"
        return f"{base_url}/{rel_posix}"
