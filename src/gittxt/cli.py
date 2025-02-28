import click
import os
import sys
from gittxt.scanner import Scanner
from gittxt.repository import RepositoryHandler
from gittxt.output_builder import OutputBuilder
from gittxt.config import ConfigManager
from gittxt.logger import Logger

# Ensure `src` is in Python's module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logger = Logger.get_logger(__name__)

# Load configuration
config = ConfigManager.load_config()

@click.command()
@click.argument("source", type=click.Path(exists=True))
@click.option("--include", multiple=True, help="Include only files matching these patterns.")
@click.option("--exclude", multiple=True, help="Exclude files matching these patterns.")
@click.option("--size-limit", type=int, help="Exclude files larger than this size (bytes).")
@click.option("--branch", type=str, help="Specify a Git branch (for remote repos).")
@click.option("--output-dir", type=click.Path(), default=config["output_dir"], show_default=True, help="Specify a custom output directory.")
@click.option("--output-format", type=click.Choice(["txt", "json", "md"], case_sensitive=False), default=config["output_format"], show_default=True, help="Specify output format.")
@click.option("--max-lines", type=int, default=config["max_lines"], show_default=True, help="Limit number of lines per file.")
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
        logger.error("❌ Failed to access repository. Check if the source path is correct.")
        return

    # Convert include/exclude patterns into lists
    include_patterns = list(include) if include else config["include_patterns"]
    exclude_patterns = list(exclude) if exclude else config["exclude_patterns"]

    # Initialize Scanner
    scanner = Scanner(
        root_path=repo_path,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        size_limit=size_limit if size_limit else config["size_limit"]
    )

    # Scan the repository
    valid_files, tree_summary = scanner.scan_directory()

    if not valid_files:
        logger.warning("⚠️ No valid files found for extraction. Ensure the repository contains supported text-based files.")
        return

    logger.info(f"✅ Processing {len(valid_files)} text files...")

    # Collect summary statistics
    total_size = sum(os.path.getsize(f) for f in valid_files)
    file_types = {os.path.splitext(f)[1] for f in valid_files}
    summary_data = {
        "total_files": len(valid_files),
        "total_size": total_size,
        "file_types": list(file_types),
    }

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
    output_file = output_builder.generate_output(valid_files, repo_path, summary_data)

    logger.info(f"✅ Output saved to: {output_file}")

    # Show Summary Report
    if summary:
        logger.info("📊 Summary Report:")
        logger.info(f" - Scanned {summary_data['total_files']} text files")
        logger.info(f" - Total Size: {summary_data['total_size']} bytes")
        logger.info(f" - File Types: {', '.join(summary_data['file_types'])}")
        logger.info(f" - Saved in: {output_file}")

if __name__ == "__main__":
    main()
