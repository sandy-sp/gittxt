import click
import os
from gittxt.scanner import Scanner
from gittxt.repository import RepositoryHandler
from gittxt.output_builder import OutputBuilder
from gittxt.config import ConfigManager
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

# Load configuration
config = ConfigManager.load_config()

@click.command()
@click.argument("source")
@click.option("--include", multiple=True, help="Include only files matching these patterns (comma-separated).")
@click.option("--exclude", multiple=True, help="Exclude files matching these patterns (comma-separated).")
@click.option("--size-limit", type=int, help="Exclude files larger than this size (bytes).")
@click.option("--branch", type=str, help="Specify a Git branch (for remote repos).")
@click.option("--output-dir", type=str, default=config["output_dir"], help="Specify a custom output directory.")
@click.option("--output-format", type=click.Choice(["txt", "json", "md"], case_sensitive=False), default=config["output_format"], help="Specify output format.")
@click.option("--max-lines", type=int, default=config["max_lines"], help="Limit number of lines per file.")
@click.option("--summary", is_flag=True, help="Show a summary report of scanned files and their types.")
@click.option("--debug", is_flag=True, help="Enable debug mode for verbose logging.")
def main(source, include, exclude, size_limit, branch, output_dir, output_format, max_lines, summary, debug):
    """Gittxt: Scan a Git repo or directory and extract text content."""

    # Enable Debug Mode
    if debug:
        logger.setLevel("DEBUG")
        logger.debug("🔍 Debug mode enabled.")

    logger.info(f"🚀 Starting Gittxt on: {source}")

    # Ensure output directory is absolute
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Handle repository (local or remote)
    repo_handler = RepositoryHandler(source, branch, reuse_existing=config["reuse_existing_repos"])
    repo_path = repo_handler.get_local_path()

    if not repo_path:
        logger.error("❌ Failed to access repository. Exiting.")
        exit(1)

    # Initialize Scanner with include and exclude patterns
    scanner = Scanner(
        root_path=repo_path,
        include_patterns=include if include else config["include_patterns"],
        exclude_patterns=exclude if exclude else config["exclude_patterns"],
        size_limit=size_limit if size_limit else config["size_limit"]
    )

    # Scan the repository
    valid_files, tree_summary = scanner.scan_directory()

    if not valid_files:
        logger.warning("⚠️ No valid files found. Exiting.")
        exit(2)

    logger.info(f"✅ Processing {len(valid_files)} files...")

    # Extract repository name for output file naming
    repo_name = os.path.basename(os.path.normpath(repo_path))

    # Initialize OutputBuilder
    output_builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=output_dir,
        max_lines=max_lines,
        output_format=output_format
    )

    # Generate output file
    output_file = output_builder.generate_output(valid_files, repo_path)

    logger.info(f"✅ Output saved to: {output_file}")

    # Show Summary Report
    if summary:
        logger.info("📊 Summary Report:")
        logger.info(f" - Scanned {len(valid_files)} text files")
        logger.info(f" - Output Format: {output_format}")
        logger.info(f" - Saved in: {output_file}")

    exit(0)

if __name__ == "__main__":
    main()
