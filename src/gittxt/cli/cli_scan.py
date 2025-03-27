import sys
import asyncio
import logging
from pathlib import Path
import click
from rich.console import Console
from gittxt.core.logger import Logger
from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.utils.file_utils import load_gittxtignore
from gittxt.utils.summary_utils import generate_summary
from .cli_utils import config
from rich.table import Table
from rich.panel import Panel
from rich import box

logger = Logger.get_logger(__name__)
console = Console()

@click.command(help="📦 Scan directories or GitHub repos (textual only).")
@click.argument("repos", nargs=-1)
@click.option("--sync", is_flag=True, default=False, help="Opt-in to .gitignore usage.")
@click.option("--exclude-dir", "-x", "exclude_dirs", multiple=True, help="Exclude folder paths.")
@click.option("--output-dir", "-o", type=click.Path(), default=None, help="Custom output directory.")
@click.option("--output-format", "-f", default="txt,json", help="Comma-separated: txt, json, md.")
@click.option("--include-patterns", "-i", multiple=True, help="Glob to include (only textual).")
@click.option("--exclude-patterns", "-e", multiple=True, help="Glob to exclude.")
@click.option("--size-limit", type=int, help="Max file size in bytes.")
@click.option("--branch", type=str, help="Git branch for remote repos.")
@click.option("--tree-depth", type=int, default=None, help="Limit tree output to N levels.")
@click.option("--debug", is_flag=True, help="Enable debug logging.")
@click.option("--zip", "create_zip", is_flag=True, help="Create a ZIP bundle.")
@click.option("--lite", is_flag=True, help="Generate minimal output instead of full content.")
def scan(
    repos,
    sync,
    exclude_dirs,
    size_limit,
    branch,
    output_dir,
    output_format,
    tree_depth,
    debug,
    create_zip,
    include_patterns,
    exclude_patterns,
    lite
):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Debug mode enabled.")

    if not repos:
        console.print("[bold red]❌ No repositories specified.[/bold red]")
        sys.exit(1)

    # Validate output formats
    allowed_formats = {"txt", "json", "md"}
    requested = {fmt.strip() for fmt in output_format.split(",")}
    if not requested.issubset(allowed_formats):
        console.print(f"[red]Invalid format. Allowed: {allowed_formats}[/red]")
        sys.exit(1)

    mode = "lite" if lite else "rich"
    final_output_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()

    asyncio.run(
        _handle_repos(
            repos,
            sync,
            exclude_dirs,
            size_limit,
            branch,
            final_output_dir,
            requested,
            tree_depth,
            create_zip,
            include_patterns,
            exclude_patterns,
            mode
        )
    )

async def _handle_repos(
    repos,
    sync,
    exclude_dirs,
    size_limit,
    branch,
    final_output_dir,
    output_formats,
    tree_depth,
    create_zip,
    include_patterns,
    exclude_patterns,
    mode
):
    for repo_source in repos:
        try:
            await _process_one_repo(
                repo_source,
                sync,
                exclude_dirs,
                size_limit,
                branch,
                final_output_dir,
                output_formats,
                tree_depth,
                create_zip,
                include_patterns,
                exclude_patterns,
                mode
            )
        except Exception as e:
            logger.error(f"❌ Failed processing {repo_source}: {e}")
            console.print(f"[red]❌ {repo_source} => {e}[/red]")

async def _process_one_repo(
    repo_source,
    sync,
    exclude_dirs,
    size_limit,
    branch,
    final_output_dir,
    output_formats,
    tree_depth,
    create_zip,
    include_patterns,
    exclude_patterns,
    mode
):
    # Decide local vs. remote
    handler = RepositoryHandler(repo_source, branch=branch)
    repo_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()
    scan_root = Path(repo_path)
    if subdir:
        scan_root = scan_root / subdir

    # Optionally load .gittxtignore if --sync
    dynamic_ignores = load_gittxtignore(scan_root) if sync else []
    merged_exclude_dirs = list(exclude_dirs) + list(dynamic_ignores)

    scanner = Scanner(
        root_path=scan_root,
        exclude_dirs=merged_exclude_dirs,
        size_limit=size_limit,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        progress=True
    )
    all_files = await scanner.scan_directory()

    if not all_files:
        console.print("[yellow]⚠️ No valid textual files found.[/yellow]")
        if is_remote:
            cleanup_temp_folder(Path(repo_path))
        return

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=final_output_dir,
        output_format=",".join(output_formats),
        repo_url=repo_source if is_remote else None,
        branch=used_branch,
        subdir=subdir
    )

    await builder.generate_output(all_files, repo_path, create_zip=create_zip, tree_depth=tree_depth, mode=mode)

    # Summary Output
    summary_data = await generate_summary(all_files)
    console.print(f"[green]✅ Scan complete for {repo_name}. {len(all_files)} files processed.[/green]")

    def render_summary_table(summary_data, repo_name):
        table = Table(title=f"📊 Gittxt Summary: {repo_name}", box=box.ROUNDED, border_style="cyan")
        table.add_column("Metric", style="bold magenta")
        table.add_column("Value", justify="right", style="green")

        table.add_row("📄 Total Files", str(summary_data["total_files"]))
        table.add_row("📦 Total Size", f'{summary_data["total_size"]:,} bytes')
        table.add_row("🔢 Estimated Tokens", f'{summary_data["estimated_tokens"]:,}')

        sub_table = Table.grid()
        sub_table.add_column("Type", style="yellow")
        sub_table.add_column("Files", justify="right")
        sub_table.add_column("Tokens", justify="right")

        breakdown = summary_data.get("file_type_breakdown", {})
        token_data = summary_data.get("tokens_by_type", {})

        for subcat in sorted(breakdown.keys()):
            sub_table.add_row(
                subcat,
                str(breakdown[subcat]),
                str(token_data.get(subcat, 0))
            )

        panel = Panel(sub_table, title="🧩 File Type Breakdown", border_style="blue")
        
        console.print(table)
        console.print(panel)

    render_summary_table(summary_data, repo_name)

    if is_remote:
        cleanup_temp_folder(Path(repo_path))
