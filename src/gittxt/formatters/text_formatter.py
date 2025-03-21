from pathlib import Path
import aiofiles
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import async_read_text

class TextFormatter:
    def __init__(self, repo_name, output_dir: Path, repo_path: Path, tree_summary: str):
        self.repo_name = repo_name
        self.output_dir = output_dir
        self.repo_path = repo_path
        self.tree_summary = tree_summary

    async def generate(self, text_files, asset_files):
        output_file = self.output_dir / f"{self.repo_name}.txt"
        summary = generate_summary(text_files + asset_files)

        async with aiofiles.open(output_file, "w", encoding="utf-8") as txt_file:
            await txt_file.write(f"=== REPO: {self.repo_name} ===\n\n")
            await txt_file.write("=== Directory Tree ===\n")
            await txt_file.write(f"{self.tree_summary}\n\n")
            await txt_file.write("=== 📊 Summary Report ===\n")
            await txt_file.write(f"Total Files: {summary['total_files']}\n")
            await txt_file.write(f"Total Size: {summary['total_size']} bytes\n")
            await txt_file.write(f"Estimated Tokens: {summary['estimated_tokens']}\n")
            for k, v in summary["file_type_breakdown"].items():
                await txt_file.write(f"{k}: {v}\n")
            await txt_file.write("\n")

            for file in text_files:
                rel = Path(file).relative_to(self.repo_path)
                content = await async_read_text(file)
                if content:
                    await txt_file.write(f"=== FILE: {rel} ===\n{content.strip()}\n\n")
        return output_file
