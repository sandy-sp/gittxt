import click
from rich.console import Console
from pathlib import Path
from gittxt.logger import Logger
from gittxt.utils.cleanup_utils import cleanup_old_outputs
from gittxt.utils.install_utils import run_interactive_install
from .cli_utils import config

logger = Logger.get_logger(__name__)
console = Console()

@click.command(help="⚙️  Run the interactive installer to configure Gittxt.")
def install():
    run_interactive_install()

@click.command(help="🔄 Remove previous scan outputs (text/json/md/zips folders).")
@click.option("--output-dir", "-o", type=click.Path(), default=None)
def clean(output_dir):
    target_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    cleanup_old_outputs(target_dir)
    console.print(f"[bold green]Cleaned output directory: {target_dir}")
