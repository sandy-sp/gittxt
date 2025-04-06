import os
import sys
import click
from rich.console import Console
from gittxt.core.reverse_engineer import reverse_from_report

console = Console()

@click.command("re")
@click.argument("report_file", type=click.Path(exists=False))
def reverse_command(report_file):
    """
    Reverse engineer a Gittxt report into reconstructed source files.
    
    Takes a Gittxt-generated report (.txt, .md, or .json) and reconstructs
    """
    if not os.path.exists(report_file):
        console.print(f"[bold red]ERROR:[/bold red] Report file not found: {report_file}")
        sys.exit(1)

    if not report_file.endswith((".txt", ".md", ".json")):
        console.print("[bold red]ERROR:[/bold red] Only .txt, .md, and .json report files are supported.")
        sys.exit(1)

    try:
        with console.status("[cyan]Reconstructing repository from report...[/cyan]"):
            zip_path = reverse_from_report(report_file)
        console.print(f"[bold green]SUCCESS:[/bold green] Reconstructed repository written to: {zip_path}")
    except Exception as e:
        console.print(f"[bold red]ERROR:[/bold red] Failed to reverse engineer report: {e}")
        sys.exit(1)

# This allows the command to be run directly
def main():
    reverse_command()

if __name__ == "__main__":
    main()

