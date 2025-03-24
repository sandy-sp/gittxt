from pathlib import Path
import sys
import asyncio
import logging
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, BarColumn
from rich.table import Table
from gittxt import __version__
from gittxt.config import ConfigManager
from gittxt.logger import Logger
from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder, cleanup_old_outputs
from gittxt.utils.filetype_utils import FiletypeConfigManager
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import load_gittxtignore

logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()
console = Console()

@click.group()
@click.version_option(version=__version__, prog_name="Gittxt CLI 🛠", hidden=True)
def cli():
    """[🚀] Gittxt CLI - Extract code & documentation from GitHub repositories."""
    pass

@cli.command(help="⚙️  Run the interactive installer to configure Gittxt.")
def install():
    from gittxt.utils.install_utils import run_interactive_install
    run_interactive_install()

@cli.group(help="🗂 Manage filetype whitelist and blacklist.")
def filetypes():
    pass

@filetypes.command("list", help="🔍 Show current whitelist and blacklist.")
def list_types():
    config = FiletypeConfigManager.load_filetype_config()
    table = Table(title="Current Whitelist & Blacklist")
    table.add_column("✅ Whitelist", style="green")
    table.add_column("❌ Blacklist", style="red")

    max_len = max(len(config.get("whitelist", [])), len(config.get("blacklist", [])))
    for i in range(max_len):
        wl = config.get("whitelist", [])[i] if i < len(config.get("whitelist", [])) else ""
        bl = config.get("blacklist", [])[i] if i < len(config.get("blacklist", [])) else ""
        table.add_row(wl, bl)
    console.print(table)

@filetypes.command(help="➕ Add extensions to whitelist.")
@click.argument("exts", nargs=-1)
def whitelist(exts):
    config = FiletypeConfigManager.load_filetype_config()
    for ext in exts:
        if ext in config.get("blacklist", []):
            config["blacklist"].remove(ext)
            console.print(f"[yellow]Removed `{ext}` from blacklist.")
        if ext not in config.get("whitelist", []):
            config["whitelist"].append(ext)
            console.print(f"[green]Added `{ext}` to whitelist.")
    FiletypeConfigManager.save_filetype_config(config)

@filetypes.command(help="🚫 Add extensions to blacklist.")
@click.argument("exts", nargs=-1)
def blacklist(exts):
    config = FiletypeConfigManager.load_filetype_config()
    for ext in exts:
        if ext in config.get("whitelist", []):
            config["whitelist"].remove(ext)
            console.print(f"[yellow]Removed `{ext}` from whitelist.")
        if ext not in config.get("blacklist", []):
            config["blacklist"].append(ext)
            console.print(f"[red]Added `{ext}` to blacklist.")
    FiletypeConfigManager.save_filetype_config(config)

@filetypes.command(help="🧹 Clear both whitelist and blacklist.")
def clear():
    FiletypeConfigManager.save_filetype_config({"whitelist": [], "blacklist": []})
    console.print("[cyan]Whitelist and blacklist cleared.")

@cli.command(help="🔄 Remove previous scan outputs (text/json/md/zips folders).")
@click.option("--output-dir", "-o", type=click.Path(), default=None)
def clean(output_dir):
    target_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    cleanup_old_outputs(target_dir)
    console.print(f"[bold green]Cleaned output directory: {target_dir}")

@click.command(help="📦 Scan one or multiple repositories or local directories.")
@click.argument("repos", nargs=-1)
@click.option("--output-dir", "-o", type=click.Path(), default=None, help="Custom output directory")
@click.option("--output-format", "-f", default="txt,json", help="txt, json, or md")
@click.option("--include", "-i", multiple=True, help="Include files matching patterns (e.g., .py)")
@click.option("--exclude", "-e", multiple=True, help="Exclude files matching patterns (e.g., node_modules)")
@click.option("--size-limit", type=int, help="Maximum file size in bytes")
@click.option("--branch", type=str, help="Specify Git branch to scan")
@click.option("--tree-depth", type=int, default=None, help="Limit tree view to N folder levels.")
@click.option("--file-types", default="all", help="Specify types: code, docs, csv, image, media, all")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--non-interactive", is_flag=True, help="Skip prompts for CI/CD workflows")
def scan(
    repos, include, exclude, size_limit, branch, output_dir, output_format, tree_depth, file_types, debug, non_interactive
):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Debug mode enabled.")

    if not repos:
        console.print("[bold red]❌ No repositories or directories specified.")
        sys.exit(1)
    
    if not non_interactive:
        console.print("[cyan]⚠️ This is an interactive session. Prompts will be shown if required.")

    allowed_formats = {"txt", "json", "md"}
    requested_formats = {fmt.strip() for fmt in output_format.split(",")}
    if not requested_formats.issubset(allowed_formats):
        console.print(f"[red]❌ Invalid output format. Allowed formats: {', '.join(allowed_formats)}")
        sys.exit(1)

    asyncio.run(
        _handle_repos(
            repos, include, exclude, size_limit, branch, output_dir, output_format, tree_depth, file_types, config
        )
    )

async def _handle_repos(repos, include, exclude, size_limit, branch, output_dir, output_format, tree_depth, file_types):
    final_output_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    include_patterns = list(include) if include else []
    exclude_patterns = list(exclude) if exclude else config.get("exclude_patterns", [])
    file_types_list = [ft.strip() for ft in file_types.split(",")]

    for repo_source in repos:
        await _process_target(repo_source, branch, include_patterns, exclude_patterns, size_limit, final_output_dir, output_format, tree_depth, file_types_list)

async def _process_target(repo_source, branch, include_patterns, exclude_patterns, size_limit, final_output_dir, output_format, tree_depth, file_types):
    # Detect local directory or Git URL
    repo_url = None
    if Path(repo_source).exists():
        repo_path = Path(repo_source).resolve()
        repo_name = repo_path.name
        is_remote = False
    else:
        repo_handler = RepositoryHandler(repo_source, branch=branch)
        repo_path, subdir, is_remote, repo_name = repo_handler.get_local_path()
        repo_path = Path(repo_path) / subdir if subdir else Path(repo_path)
        repo_url = repo_source.split(".git")[0] if ".git" in repo_source else repo_source

    # Load .gittxtignore if present
    gittxtignore_patterns = load_gittxtignore(repo_path)
    if gittxtignore_patterns:
        console.print(f"[cyan]📄 Loaded {len(gittxtignore_patterns)} patterns from .gittxtignore")

    # Merge all exclude patterns
    merged_excludes = list(set(exclude_patterns + gittxtignore_patterns + config.get("exclude_patterns", [])))

    # Scanner instantiation
    scanner = Scanner(
        root_path=repo_path,
        include_patterns=include_patterns,
        exclude_patterns=merged_excludes,
        size_limit=size_limit,
        file_types=file_types,
        progress=True
    )

    all_files = await scanner.scan_directory()

    if not all_files:
        console.print("[yellow]⚠️ No valid files found. Skipping...")
        if is_remote:
            cleanup_temp_folder(repo_path)
        return

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=final_output_dir,
        output_format=output_format,
        repo_url=repo_url
    )

    await builder.generate_output(all_files, repo_path, create_zip=False, tree_depth=tree_depth)

    summary_data = generate_summary(all_files)
    _print_summary(repo_name, summary_data, final_output_dir)

    if is_remote:
        cleanup_temp_folder(repo_path)

    logger.info("✅ Gittxt scan completed.")

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
    console.print(f"[green]Tip:[/] Run 'gittxt zip {repo_name}' to create ZIP package.")

if __name__ == "__main__":
    cli()
