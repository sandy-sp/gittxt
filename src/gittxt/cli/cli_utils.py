from rich.console import Console
from rich.table import Table
from gittxt.core.config import ConfigManager

config = ConfigManager.load_config()
console = Console()

def _print_summary(repo_name, summary_data, final_output_dir, output_format):
    table = Table(title=f"Scan Summary: {repo_name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Total Files", str(summary_data.get("total_files")))
    table.add_row("Total Size (bytes)", str(summary_data.get("total_size")))
    table.add_row("Estimated Tokens", str(summary_data.get("estimated_tokens")))
    table.add_row("Output Formats", output_format)
    console.print(table)
    console.print(f"[bold yellow]Output directory:[/] {final_output_dir / repo_name}")
