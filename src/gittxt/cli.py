from pathlib import Path
import click
import sys
import logging
import asyncio
from gittxt.config import ConfigManager
from gittxt.logger import Logger
from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder, cleanup_old_outputs
from gittxt.utils.filetype_utils import classify_file, FiletypeConfigManager
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.summary_utils import generate_summary

logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

@click.group()
def cli():
    """Gittxt CLI: Scan and extract text/code from GitHub repositories."""
    pass

@cli.command()
def install():
    from gittxt.utils.install_utils import run_interactive_install
    run_interactive_install()

@cli.command()
@click.argument("repo", type=str)
@click.option("--tree-depth", type=int, default=None, help="Limit tree view to N folder levels.")
def tree(repo, tree_depth):
    repo_handler = RepositoryHandler(repo)
    repo_path, subdir, is_remote, _ = repo_handler.get_local_path()
    if not repo_path:
        click.echo("❌ Could not resolve repository.")
        sys.exit(1)

    scan_root = Path(repo_path) / subdir if subdir else Path(repo_path)
    tree_output = generate_tree(scan_root, max_depth=tree_depth)
    click.echo(tree_output)

    cleanup_temp_folder(Path(repo_path)) if repo_handler.is_remote else None

@cli.command()
@click.argument("file", type=click.Path(exists=True))
def classify(file):
    fpath = Path(file)
    result = classify_file(fpath)
    click.echo(f"📄 `{fpath}` classified as: {result}")

@cli.command()
@click.argument("ext", type=str)
def whitelist(ext):
    FiletypeConfigManager.add_to_whitelist(ext)
    click.echo(f"✅ Added `{ext}` to whitelist.")

@cli.command()
@click.argument("ext", type=str)
def blacklist(ext):
    FiletypeConfigManager.add_to_blacklist(ext)
    click.echo(f"✅ Added `{ext}` to blacklist.")

@cli.command()
@click.option("--output-dir", type=click.Path(), default=None)
def clean(output_dir):
    target_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    cleanup_old_outputs(target_dir)
    click.echo(f"🗑️ Cleaned output directory: {target_dir}")

@cli.command()
@click.argument("repos", nargs=-1)
@click.option("--include", multiple=True, help="Include files matching patterns (e.g., .py)")
@click.option("--exclude", multiple=True, help="Exclude files matching patterns (e.g., node_modules)")
@click.option("--size-limit", type=int, help="Maximum file size in bytes")
@click.option("--branch", type=str, help="Specify Git branch to scan")
@click.option("--output-dir", type=click.Path(), default=None)
@click.option("--output-format", default="txt", help="txt, json, md, or comma-separated list")
@click.option("--summary", is_flag=True, help="Show summary report after scan")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--progress", is_flag=True, help="Show scan progress bar")
@click.option("--non-interactive", is_flag=True, help="Skip prompts (CI/CD friendly)")
@click.option("--tree-depth", type=int, default=None, help="Limit tree view to N folder levels.")
@click.option("--zip", "create_zip", is_flag=True, help="Generate ZIP bundle with outputs + assets (CI-friendly)")
@click.option("--file-types", default="code,docs", help="Specify types: code, docs, csv, image, media, all")
def scan(
    repos,
    include,
    exclude,
    size_limit,
    branch,
    output_dir,
    output_format,
    summary,
    debug,
    progress,
    non_interactive,
    tree_depth,
    create_zip,
    file_types
):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Debug mode enabled.")

    if not repos:
        logger.error("❌ No repositories specified.")
        click.echo("❌ No repositories specified.")
        sys.exit(1)

    final_output_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    include_patterns = list(include) if include else []
    exclude_patterns = list(exclude) if exclude else config.get("exclude_patterns", [])
    file_types = [ft.strip() for ft in file_types.split(",")]

    VALID_FILETYPES = {"code", "docs", "csv", "image", "media", "all"}
    for ft in file_types:
        if ft not in VALID_FILETYPES:
            logger.error(f"❌ Invalid file type: {ft}. Valid options: {', '.join(VALID_FILETYPES)}")
            sys.exit(1)

    logger.info(f"🧹 Applying exclude filters: {exclude_patterns or 'None'}")

    for repo_source in repos:
        _process_repo(
            repo_source, branch, include_patterns, exclude_patterns, size_limit,
            final_output_dir, output_format, summary, debug, progress, non_interactive, tree_depth, create_zip, file_types
        )

def _process_repo(
    repo_source, branch, include_patterns, exclude_patterns, size_limit,
    final_output_dir, output_format, summary, debug, progress, non_interactive, tree_depth, create_zip, file_types
):
    logger.info(f"🚀 Processing repository: {repo_source}")
    repo_handler = RepositoryHandler(repo_source, branch=branch)
    repo_path, subdir, is_remote, repo_name = repo_handler.get_local_path()
    if not repo_path:
        logger.error("❌ Repository resolution failed.")
        sys.exit(1)

    scan_root = Path(repo_path) / subdir if subdir else Path(repo_path)

    # If remote, construct GitHub URL prefix
    repo_url = None
    if is_remote and "github.com" in repo_source:
        repo_url = repo_source.split(".git")[0] if ".git" in repo_source else repo_source

    scanner = Scanner(
        root_path=scan_root,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        size_limit=size_limit,
        file_types=file_types,
        progress=progress,
    )

    all_files, tree_output = scanner.scan_directory()

    if not all_files:
        logger.warning("⚠️ No valid files found. Skipping...")
        if is_remote:
            cleanup_temp_folder(Path(repo_path))
        return

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=final_output_dir,
        output_format=output_format,
        repo_url=repo_url
    )

    if not non_interactive:
        final_zip = click.confirm("📦 Do you want to generate a ZIP bundle with outputs + assets?", default=create_zip)
    else:
        final_zip = create_zip

    asyncio.run(builder.generate_output(all_files, repo_path, create_zip=final_zip, tree_depth=tree_depth))

    if summary:
        summary_data = generate_summary(all_files)
        logger.info("📊 Summary Report:")
        logger.info(f" - Total files: {summary_data.get('total_files')}")
        logger.info(f" - Total size (bytes): {summary_data.get('total_size')}")
        logger.info(f" - Estimated tokens: {summary_data.get('estimated_tokens')}")
        logger.info(f" - File type breakdown: {summary_data.get('file_type_breakdown')}")
        logger.info(f" - Output formats: {output_format}")

    if is_remote:
        cleanup_temp_folder(Path(repo_path))

    logger.info("✅ Gittxt scan completed.\n")

def main():
    cli()

if __name__ == "__main__":
    main()
