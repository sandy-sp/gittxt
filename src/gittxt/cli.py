import click
import os
import sys
from gittxt.scanner import Scanner
from gittxt.repository import RepositoryHandler
from gittxt.output_builder import OutputBuilder
from gittxt.config import load_config
from gittxt.logger import get_logger

logger = get_logger(__name__)

@click.command()
@click.argument("source")
@click.option("--include", multiple=True, help="Include only files matching these patterns (comma-separated).")
@click.option("--exclude", multiple=True, help="Exclude files matching these patterns (comma-separated).")
@click.option("--size-limit", type=int, help="Exclude files larger than this size (bytes).")
@click.option("--branch", type=str, help="Specify a Git branch (for remote repos).")
@click.option("--output-dir", type=str, help="Specify a custom output directory.")
@click.option("--output-format", type=click.Choice(["txt", "json"], case_sensitive=False), help="Specify output format.")
@click.option("--max-lines", type=int, help="Limit number of lines per file.")
@click.option("--config", type=str, help="Specify a custom config file path.")
@click.option("--force-rescan", is_flag=True, help="Clear cache and force a full rescan.")
def main(source, include, exclude, size_limit, branch, output_dir, output_format, max_lines, config, force_rescan):
    """Gittxt: Scan a Git repo and extract text content."""
    
    # Load configuration from user-specified file or default
    config = load_config(config_path=config)

    # Use CLI arguments if provided; otherwise, fallback to config values
    output_dir = output_dir or config["output_dir"]
    size_limit = size_limit if size_limit is not None else config["size_limit"]
    include_patterns = list(include) if include else config["include_patterns"]
    exclude_patterns = list(exclude) if exclude else config["exclude_patterns"]
    output_format = output_format or config["output_format"]
    max_lines = max_lines if max_lines is not None else config["max_lines"]

    click.echo(f"🚀 Starting Gittxt on: {source}")
    sys.stdout.flush()  # Ensure output is printed immediately
    logger.info(f"Starting Gittxt on: {source}")

    # Handle repository (local or remote)
    repo_handler = RepositoryHandler(source, branch)
    repo_path = repo_handler.get_local_path()

    if not os.path.exists(source):
        click.echo("❌ Repository path does not exist. Exiting.")
        sys.stdout.flush()
        logger.error("❌ Repository path does not exist.")
        sys.exit(1)


    # Extract repository name for output file naming
    repo_name = os.path.basename(os.path.normpath(repo_path))

    # Initialize Scanner with repo_name
    scanner = Scanner(
        repo_name=repo_name,
        root_path=repo_path,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        size_limit=size_limit
    )

    # Clear cache if --force-rescan is used
    if force_rescan:
        scanner.cache = {}  # Reset cache
        scanner.save_cache()  # Ensure cache is saved as empty
        click.echo(f"♻️ Cache reset for {repo_name}. Performing a full rescan.")
        sys.stdout.flush()
        logger.info(f"♻️ Cache reset for {repo_name}. Performing a full rescan.")

    # Scan the repository
    valid_files = scanner.scan_directory()

    if not valid_files:
        click.echo("⚠️ No valid files found. Exiting.")
        sys.stdout.flush()
        logger.warning("⚠️ No valid files found. Exiting.")
        sys.exit(1)

    click.echo(f"✅ Processing {len(valid_files)} files...")
    sys.stdout.flush()
    logger.info(f"✅ Processing {len(valid_files)} files...")

    # Initialize OutputBuilder
    output_builder = OutputBuilder(
        repo_name=repo_name,
        max_lines=max_lines,
        output_format=output_format
    )

    # Generate output file
    output_file = output_builder.generate_output(valid_files, repo_path)

    click.echo(f"✅ Output saved to: {output_file}")
    sys.stdout.flush()
    logger.info(f"✅ Output saved to: {output_file}")

if __name__ == "__main__":
    main()
