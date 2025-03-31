from rich.console import Console
from rich.table import Table
from gittxt.core.config import ConfigManager

config = ConfigManager.load_config()
console = Console()

def _print_summary(repo_name, summary_data, final_output_dir, output_format):
    output_path = final_output_dir / repo_name
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        console.print(f"[red]❌ Cannot create output directory {output_path}: {e}")
        return

    table = Table(title=f"Scan Summary: {repo_name}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    total_files = summary_data.get("total_files", 0)
    total_size = summary_data.get("formatted", {}).get(
        "total_size", f"{summary_data.get('total_size', 0):,} bytes"
    )
    estimated_tokens = summary_data.get("estimated_tokens", 0)

    table.add_row("Total Files", str(total_files))
    table.add_row("Total Size", total_size)
    table.add_row("Estimated Tokens", f"{estimated_tokens:,}")

    if isinstance(output_format, (list, set)):
        fmt_display = ", ".join(output_format)
    else:
        fmt_display = str(output_format)
    table.add_row("Output Formats", fmt_display)

    console.print(table)
    console.print(f"[bold yellow]Output directory:[/] {output_path}")
