from rich.console import Console
from rich.table import Table
from gittxt.core.config import ConfigManager
import click
from pathlib import Path
from gittxt.utils.cleanup_utils import cleanup_old_outputs

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


@click.command(help="🔄 Remove previous scan outputs (including text/json/md/zips).")
@click.option("--output-dir", "-o", type=click.Path(), default=None)
def clean(output_dir):
    target_dir = (
        Path(output_dir).resolve()
        if output_dir
        else Path(config.get("output_dir")).resolve()
    )
    cleanup_old_outputs(target_dir)
    console.print(f"[bold green]Cleaned output directory: {target_dir}")
    if not target_dir.exists():
        console.print(f"[red]❌ Output directory does not exist: {target_dir}[/red]")
        return
