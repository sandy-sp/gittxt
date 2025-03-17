from pathlib import Path
import click
import sys
import logging

from gittxt.config import ConfigManager
from gittxt.logger import Logger
from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder, zip_files
from gittxt.utils.filetype_utils import classify_file

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
@click.argument("repos", nargs=-1)
@click.option("--include", multiple=True, help="Include files matching patterns (e.g., .py)")
@click.option("--exclude", multiple=True, help="Exclude files matching patterns (e.g., node_modules)")
@click.option("--size-limit", type=int, help="Maximum file size in bytes")
@click.option("--branch", type=str, help="Specify Git branch to scan")
@click.option("--output-dir", type=click.Path(), default=None)
@click.option("--output-format", default="txt", help="txt, json, md, or comma-separated list")
@click.option("--file-types", default="code,docs", help="code,docs,images,csv,media,all")
@click.option("--summary", is_flag=True, help="Show summary report after scan")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--progress", is_flag=True, help="Show scan progress bar")
@click.option("--non-interactive", is_flag=True, help="Skip prompts (CI/CD friendly)")
def scan(repos, include, exclude, size_limit, branch, output_dir,
         output_format, file_types, summary, debug, progress, non_interactive):
    """Scan one or more repositories (local or remote)"""

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Debug mode enabled.")

    if not repos:
        click.echo("❌ No repositories specified.")
        sys.exit(1)

    final_output_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    include_patterns = list(include) if include else []
    exclude_patterns = list(exclude) if exclude else []

    logger.info("🧹 Applying default filters: ['.git', '__pycache__', 'node_modules', '.log']")

    # Interactive inclusion prompt (optional)
    if not non_interactive:
        click.echo(f"Selected file types to include: {file_types}")
        if click.confirm("Do you want to include images or CSVs in the output?", default=False):
            file_types = "all"

    for repo_source in repos:
        logger.info(f"🚀 Processing repository: {repo_source}")
        repo_handler = RepositoryHandler(repo_source, branch=branch)
        repo_path, subdir, is_remote = repo_handler.get_local_path()
        scan_root = Path(repo_path) / subdir if subdir else Path(repo_path)
        scanner = Scanner(
            root_path=scan_root,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            size_limit=size_limit,
            file_types=file_types.split(","),
            progress=progress
        )

        valid_files, tree_summary = scanner.scan_directory()
        if not valid_files:
            logger.warning("⚠️ No valid files found. Skipping...")
            cleanup_temp_folder(Path(repo_path))
            continue

        repo_name = Path(repo_path).name
        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=final_output_dir,
            output_format=output_format
        )

        generated_files = builder.generate_output(valid_files, scan_root)

        # Zip non-code assets (images/csvs)
        if "all" in file_types or "images" in file_types or "csv" in file_types:
            zip_path = final_output_dir / f"{repo_name}_extras.zip"
            zip_files([Path(f) for f in valid_files], zip_path)
            logger.info(f"📦 Packaged non-code assets into: {zip_path}")

        if summary:
            total_types = {}
            for f in valid_files:
                ftype = classify_file(Path(f))
                total_types[ftype] = total_types.get(ftype, 0) + 1

            logger.info("📊 Summary Report:")
            logger.info(f" - Total files processed: {len(valid_files)}")
            logger.info(f" - Output formats: {output_format}")
            logger.info(f" - File type breakdown: {total_types}")

        if is_remote:
            cleanup_temp_folder(Path(repo_path))

        logger.info("✅ Gittxt scan completed.\n")


def main():
    cli()

if __name__ == "__main__":
    main()
