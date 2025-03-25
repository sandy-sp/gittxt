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
from .cli_utils import config, _print_summary

logger = Logger.get_logger(__name__)
console = Console()

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
        console.print("[cyan]⚠️ Interactive mode enabled.")

    allowed_formats = {"txt", "json", "md"}
    requested_formats = {fmt.strip() for fmt in output_format.split(",")}
    if not requested_formats.issubset(allowed_formats):
        console.print(f"[red]❌ Invalid output format. Allowed: {', '.join(allowed_formats)}")
        sys.exit(1)

    asyncio.run(
        _handle_repos(
            repos, include, exclude, size_limit, branch, output_dir, output_format, tree_depth, file_types
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

    gittxtignore_patterns = load_gittxtignore(repo_path)
    merged_excludes = list(set(exclude_patterns + gittxtignore_patterns + config.get("exclude_patterns", [])))

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

    summary_data = await generate_summary(all_files)
    _print_summary(repo_name, summary_data, final_output_dir, output_format)

    if is_remote:
        cleanup_temp_folder(repo_path)

    logger.info("✅ Gittxt scan completed.")
