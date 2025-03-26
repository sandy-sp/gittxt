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
from gittxt.utils.repo_url_parser import parse_github_url

logger = Logger.get_logger(__name__)
console = Console()

@click.command(help="📦 Scan local dirs or GitHub repos, capturing TEXT ONLY. e.g.\n  gittxt scan https://github.com/sandy-sp/gittxt --output-format txt,json")
@click.argument("repos", nargs=-1)
@click.option("--exclude-dir", "-x", "exclude_dirs", multiple=True, help="Exclude folder paths (e.g., node_modules, .git)")
@click.option("--output-dir", "-o", type=click.Path(), default=None, help="Custom output directory")
@click.option("--output-format", "-f", default="txt,json", help="txt, json, or md")
@click.option("--include-patterns", "-i", multiple=True, help="Include only files matching these glob patterns (applies to TEXTUAL files only)")
@click.option("--exclude-patterns", "-e", multiple=True, help="Exclude files matching these glob patterns (e.g. *.log)")
@click.option("--size-limit", type=int, help="Maximum file size in bytes")
@click.option("--branch", type=str, help="Specify Git branch to scan (GitHub URLs)")
@click.option("--tree-depth", type=int, default=None, help="Limit tree view to N folder levels.")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--non-interactive", is_flag=True, help="Skip prompts for CI/CD workflows")
@click.option("--zip", "create_zip", is_flag=True, help="Create zipped output bundle")
@click.option("--lite", is_flag=True, help="Generate minimal output (tree + code only)")
def scan(
    repos, exclude_dirs, size_limit, branch, output_dir, output_format,
    tree_depth, debug, non_interactive, create_zip,
    include_patterns, exclude_patterns, lite
):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Debug mode enabled.")

    if not repos:
        raise click.ClickException("[bold red]❌ No repositories or directories specified.")

    if not non_interactive:
        console.print("[cyan]⚠️ Interactive mode enabled.")

    allowed_formats = {"txt", "json", "md"}
    requested_formats = {fmt.strip() for fmt in output_format.split(",")}
    if not requested_formats.issubset(allowed_formats):
        raise click.ClickException(f"Invalid output format. Allowed: {', '.join(allowed_formats)}")

    asyncio.run(
        _handle_repos(
            repos, exclude_dirs, size_limit, branch, output_dir,
            output_format, tree_depth, create_zip=create_zip or config.get("auto_zip", False),
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            lite=lite
        )
    )

async def _handle_repos(repos, exclude_dirs, size_limit, branch, output_dir,
                        output_format, tree_depth, create_zip,
                        include_patterns, exclude_patterns, lite):
    final_output_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    exclude_dirs = list(exclude_dirs) if exclude_dirs else config.get("exclude_dirs", [])

    for repo_source in repos:
        try:
            await _process_target(
                repo_source, include_patterns, exclude_patterns, branch, exclude_dirs,
                size_limit, final_output_dir, output_format, tree_depth,
                create_zip=create_zip, mode="lite" if lite else "rich"
            )
        except Exception as e:
            logger.error(f"❌ Failed to process {repo_source}: {e}")
            console.print(f"[red]❌ Failed to scan {repo_source}: {e}")

async def _process_target(repo_source, include_patterns, exclude_patterns, branch,
                          exclude_dirs, size_limit, final_output_dir, output_format,
                          tree_depth, create_zip, mode):
    # Local or remote
    if Path(repo_source).exists():
        repo_path = Path(repo_source).resolve()
        repo_name = repo_path.name
        is_remote = False
        repo_url = f"file://{repo_path}"
        logger.debug(f"Local repository resolved: {repo_path} (repo_url: {repo_url})")
    else:
        parsed = parse_github_url(repo_source)
        repo_handler = RepositoryHandler(repo_source, branch=branch)
        repo_path, subdir, is_remote, repo_name = repo_handler.get_local_path()
        repo_path = Path(repo_path) / subdir if subdir else Path(repo_path)
        base = f"https://github.com/{parsed['owner']}/{parsed['repo']}"
        branch_used = parsed.get("branch") or "main"
        subdir_used = parsed.get("subdir", "").strip("/")
        if subdir_used:
            repo_url = f"{base}/tree/{branch_used}/{subdir_used}"
        else:
            repo_url = f"{base}/tree/{branch_used}"
        logger.debug(f"Remote repository resolved: {repo_path} (repo_url: {repo_url})")

    gittxtignore_patterns = load_gittxtignore(repo_path)
    merged_excludes = list(set(exclude_dirs + gittxtignore_patterns + config.get("exclude_dirs", [])))

    # Strict textual scanning
    scanner = Scanner(
        root_path=repo_path,
        exclude_dirs=merged_excludes,
        size_limit=size_limit,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
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
    await builder.generate_output(all_files, repo_path, create_zip=create_zip, tree_depth=tree_depth, mode=mode)

    summary_data = await generate_summary(all_files)
    _print_summary(repo_name, summary_data, final_output_dir, output_format)

    if is_remote:
        cleanup_temp_folder(repo_path)

    logger.info("✅ Gittxt scan completed.")
