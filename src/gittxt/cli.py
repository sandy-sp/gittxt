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
from gittxt.utils.filetype_utils import classify_simple
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
    """Run interactive config setup"""
    from gittxt.utils.install_utils import run_interactive_install
    run_interactive_install()

@cli.command()
@click.argument("repo", type=click.Path(exists=True))
def classify(repo):
    """Classify all files in a given repository or folder."""
    repo_path = Path(repo)
    files = repo_path.rglob("*") if repo_path.is_dir() else [repo_path]
    for file in files:
        if file.is_file():
            category, subcat = classify_simple(file)
            click.echo(f"📄 {file} ➡ {category} / {subcat}")

@cli.command()
@click.option("--output-dir", "-o", type=click.Path(), default=None, help="Custom output directory")
def clean(output_dir):
    """Delete old outputs (text/json/md/zips folders)."""
    target_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    cleanup_old_outputs(target_dir)
    click.echo(f"🗑️ Cleaned output directory: {target_dir}")

@cli.command()
@click.argument("repos", nargs=-1)
@click.option("--include", "-i", multiple=True, help="Include files matching patterns (e.g., .py)")
@click.option("--exclude", "-e", multiple=True, help="Exclude files matching patterns (e.g., node_modules)")
@click.option("--size-limit", type=int, help="Maximum file size in bytes")
@click.option("--branch", type=str, help="Specify Git branch to scan")
@click.option("--output-dir", "-o", type=click.Path(), default=None)
@click.option("--output-format", "-f", default="txt", help="txt, json, md, or comma-separated list")
@click.option("--summary", is_flag=True, help="Show summary report after scan")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--progress", is_flag=True, help="Show scan progress bar")
@click.option("--non-interactive", is_flag=True, help="Skip prompts (CI/CD friendly)")
@click.option("--tree-depth", type=int, default=None, help="Limit tree view to N folder levels.")
@click.option("--zip", "create_zip", is_flag=True, help="Generate ZIP bundle with outputs + assets")
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
    create_zip
):
    """Scan one or more repositories (local or remote)"""
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

    for repo_source in repos:
        _process_repo(
            repo_source, branch, include_patterns, exclude_patterns, size_limit,
            final_output_dir, output_format, summary, debug, progress, non_interactive, tree_depth, create_zip
        )

def _process_repo(
    repo_source, branch, include_patterns, exclude_patterns, size_limit,
    final_output_dir, output_format, summary, debug, progress, non_interactive, tree_depth, create_zip
):
    logger.info(f"🚀 Processing repository: {repo_source}")
    repo_handler = RepositoryHandler(repo_source, branch=branch)
    repo_path, subdir, is_remote, repo_name = repo_handler.get_local_path()
    if not repo_path:
        logger.error("❌ Repository resolution failed.")
        sys.exit(1)

    scan_root = Path(repo_path) / subdir if subdir else Path(repo_path)

    scanner = Scanner(
        root_path=scan_root,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        size_limit=size_limit,
        file_types=["all"],
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
    )

    if not non_interactive:
        final_zip = click.confirm("📦 Generate ZIP bundle with outputs + assets?", default=create_zip)
    else:
        final_zip = create_zip

    asyncio.run(builder.generate_output(all_files, repo_path, create_zip=final_zip, tree_depth=tree_depth))

    if summary:
        summary_data = generate_summary(all_files)
        click.echo("\n📊 Summary Report:")
        click.echo(f" - Total files: {summary_data.get('total_files')}")
        click.echo(f" - Total size: {summary_data.get('total_size')} bytes")

        click.echo("\nTEXTUAL Files:")
        for k, v in summary_data["TEXTUAL"].items():
            if k != "estimated_tokens" and k != "tokens_by_type":
                click.echo(f" - {k}: {v}")
        click.echo(f" - Estimated tokens: {summary_data['TEXTUAL']['estimated_tokens']}")

        click.echo("\nNON-TEXTUAL Files:")
        for k, v in summary_data["NON-TEXTUAL"].items():
            click.echo(f" - {k}: {v}")

    if is_remote:
        cleanup_temp_folder(Path(repo_path))

    logger.info("✅ Gittxt scan completed.\n")


def main():
    cli()

if __name__ == "__main__":
    main()
