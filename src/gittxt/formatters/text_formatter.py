from pathlib import Path
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text
from gittxt.utils.filetype_utils import classify_simple
from datetime import datetime, timezone

class TextFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str, repo_url: str = None):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary
        self.repo_url = repo_url

    async def generate(self, text_files, non_textual_files):
        output_file = self.output_dir / f"{self.repo_name}.txt"
        summary = generate_summary(text_files + non_textual_files)

        ordered_files = self._sort_textual_files(text_files)

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
                rel = Path(file).relative_to(self.repo_path)
                primary, subcat = classify_simple(file)
                content = await async_read_text(file)
                token_est = summary.get("tokens_by_type", {}).get(subcat, 0)
                if content:
                    await txt_file.write(f"\n---\nFILE: {rel} | TYPE: {subcat} | SIZE: {file.stat().st_size} bytes | TOKENS: {token_est}\n---\n")
                    await txt_file.write(f"{content.strip()}\n")

            await txt_file.write("\n=== 🎨 Non-Textual Assets ===\n")
            for asset in non_textual_files:
                rel = Path(asset).relative_to(self.repo_path)
                primary, subcat = classify_simple(asset)
                asset_url = self._build_github_url(rel) if self.repo_url else ""
                await txt_file.write(f"{rel} | TYPE: {subcat} | SIZE: {asset.stat().st_size} bytes {asset_url}\n")

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

    def _build_github_url(self, rel_path: Path) -> str:
        return f"| {self.repo_url}/blob/main/{rel_path.as_posix()}"
