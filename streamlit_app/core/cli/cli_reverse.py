import os
import sys
import click
from pathlib import Path
from rich.console import Console
from core.core.reverse_engineer import reverse_from_report
from core.core.config import ConfigManager

console = Console()
config = ConfigManager.load_config()

@click.command("re")
@click.argument("report_file", type=click.Path(exists=False))
@click.option("--output-dir", "-o", type=click.Path(), default=None, 
              help="Custom output directory for reconstructed files.")
def reverse_command(report_file, output_dir):
    """
    Reverse engineer a Gittxt report into reconstructed source files.

    Takes a Gittxt-generated report (.txt, .md, or .json) and reconstructs
    the original file structure as a ZIP archive.
    """
    if not os.path.exists(report_file):
        console.print(f"[bold red]ERROR:[/bold red] Report file not found: {report_file}")
        sys.exit(1)

    if not report_file.endswith((".txt", ".md", ".json")):
        console.print("[bold red]ERROR:[/bold red] Only .txt, .md, and .json report files are supported.")
        sys.exit(1)

    # Convert output_dir to Path if provided
    output_path = Path(output_dir) if output_dir else None

    try:
        with console.status("[cyan]Reconstructing repository from report...[/cyan]"):
            zip_path = reverse_from_report(report_file, output_path)

        console.print(f"[bold green]SUCCESS:[/bold green] Reconstructed repository written to: {zip_path}")

        # Optional warning if report might be partial (from --lite or --no-tree)
        if report_file.endswith(".json"):
            with open(report_file, "r", encoding="utf-8") as f:
                import json
                try:
                    data = json.load(f)
                    if "tree_summary" not in data.get("repository", {}):
                        console.print("[yellow]⚠️ Note: This report did not include a directory tree. Reconstructed structure may be limited.[/yellow]")
                    if not data.get("assets"):
                        console.print("[yellow]⚠️ Note: No non-textual assets were included in this report.[/yellow]")
                except Exception:
                    pass

    except Exception as e:
        console.print(f"[bold red]ERROR:[/bold red] Failed to reverse engineer report: {e}")
        sys.exit(1)


def main():
    reverse_command()

if __name__ == "__main__":
    main()
