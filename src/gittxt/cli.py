from pathlib import Path
import click
import sys
import logging

from gittxt.config import ConfigManager
from gittxt.logger import Logger
from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder, cleanup_old_outputs
from gittxt.utils.filetype_utils import classify_file, update_whitelist, update_blacklist
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.summary_utils import generate_summary

logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

@click.group()
def cli():
    """Gittxt CLI: Scan and extract text/code from GitHub repositories."""
    pass

@click.command()
@click.argument("repo", type=str)
@click.option("--tree-depth", type=int, default=None, help="Limit tree view to N folder levels.")
def tree(repo, tree_depth):
    """Show folder structure for a repo (local or remote)."""
    repo_handler = RepositoryHandler(repo)
    repo_path, subdir, _ = repo_handler.get_local_path()
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
    """Classify a single file (text/code/asset)."""
    fpath = Path(file)
    result = classify_file(fpath)
    click.echo(f"📄 `{fpath}` classified as: {result}")

@cli.command()
@click.option("--output-dir", type=click.Path(), default=None)
def clean(output_dir):
    """Delete old outputs (text/json/md/zips folders)."""
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
    tree_depth
):
    """Scan one or more repositories (local or remote)"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Debug mode enabled.")

    if not repos:
        click.echo("❌ No repositories specified.")
        sys.exit(1)

    final_output_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    include_patterns = list(include) if include else []
    exclude_patterns = list(exclude) if exclude else config.get("exclude_patterns", [])

    logger.info(f"🧹 Applying exclude filters: {exclude_patterns or 'None'}")

    for repo_source in repos:
        _process_repo(
            repo_source, branch, include_patterns, exclude_patterns, size_limit,
            final_output_dir, output_format, summary, debug, progress, non_interactive, tree_depth
        )


def _process_repo(
    repo_source, branch, include_patterns, exclude_patterns, size_limit,
    final_output_dir, output_format, summary, debug, progress, non_interactive, tree_depth
):
    logger.info(f"🚀 Processing repository: {repo_source}")
    repo_handler = RepositoryHandler(repo_source, branch=branch)
    repo_path, subdir, is_remote = repo_handler.get_local_path()
    if not repo_path:
        logger.error("❌ Repository resolution failed.")
        return

    scan_root = Path(repo_path) / subdir if subdir else Path(repo_path)

    scanner = Scanner(
        root_path=scan_root,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        size_limit=size_limit,
        file_types=["all"],  # Dynamically classified
        progress=progress,
    )

    all_files, tree_output = scanner.scan_directory()

    # Apply user-defined max depth to CLI output tree
    tree_output = generate_tree(scan_root, max_depth=tree_depth)

    if not all_files:
        logger.warning("⚠️ No valid files found. Skipping...")
        if is_remote:
            cleanup_temp_folder(Path(repo_path))
        return

    text_files, asset_files = [], []

    for file in all_files:
        ext = Path(file).suffix.lower()
        classification = classify_file(Path(file))

        if classification == "text":
            logger.info(f"[AUTO-INCLUDED] as TEXT: {file}")
            text_files.append(file)
        else:
            logger.info(f"[AUTO-EXCLUDED] as ASSET: {file}")
            asset_files.append(file)

            if not non_interactive and ext not in config.get("blacklist", []) and ext not in config.get("whitelist", []):
                click.echo(f"\n🤖 Detected unknown extension `{ext}` in {file}")
                if click.confirm("➕ Add to whitelist (processable)?", default=False):
                    update_whitelist(ext)
                    logger.info(f"[✔️] Extension `{ext}` added to whitelist.")
                elif click.confirm("➖ Add to blacklist (always skip)?", default=False):
                    update_blacklist(ext)
                    logger.info(f"[✔️] Extension `{ext}` added to blacklist.")

    repo_name = Path(repo_path).name
    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=final_output_dir,
        output_format=output_format,
    )

    create_zip = False
    if not non_interactive:
        create_zip = click.confirm("📦 Do you want to generate a ZIP bundle with outputs + assets?", default=False)

    asyncio.run(builder.generate_output(text_files + asset_files, repo_path, create_zip=create_zip))

    if summary:
        summary_data = generate_summary(text_files + asset_files)
        logger.info("📊 Summary Report:")
        logger.info(f" - Total files: {summary_data.get('total_files')}")
        logger.info(f" - Text files: {summary_data.get('text_files')}")
        logger.info(f" - Asset files: {summary_data.get('asset_files')}")
        logger.info(f" - Total size (bytes): {summary_data.get('total_size')}")
        logger.info(f" - Estimated tokens: {summary_data.get('estimated_tokens')}")
        logger.info(f" - Output formats: {output_format}")


    if is_remote:
        cleanup_temp_folder(Path(repo_path))

    logger.info("✅ Gittxt scan completed.\n")

def main():
    cli()

if __name__ == "__main__":
    main()
