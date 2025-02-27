import click
import os
from gittxt.scanner import Scanner
from gittxt.repository import RepositoryHandler
from gittxt.output_builder import OutputBuilder
from gittxt.logger import get_logger

logger = get_logger(__name__)

@click.command()
@click.argument("source")
@click.option("--include", multiple=True, help="Include only files matching this pattern (e.g., '.py')")
@click.option("--exclude", multiple=True, help="Exclude files matching this pattern")
@click.option("--size-limit", type=int, help="Exclude files larger than this size (bytes)")
@click.option("--branch", type=str, help="Specify a Git branch (for remote repos)")
@click.option("--format", type=click.Choice(["txt", "json"], case_sensitive=False), default="txt", help="Specify output format")
@click.option("--max-lines", type=int, help="Limit number of lines per file")
@click.option("--force-rescan", is_flag=True, help="Ignore cache and perform a full rescan")
def main(source, include, exclude, size_limit, branch, format, max_lines, force_rescan):
    """Gittxt: Scan a Git repo and extract text content."""

    logger.info(f"🔍 Initializing Gittxt for source: {source}")

    # Handle repository (local or remote)
    repo_handler = RepositoryHandler(source, branch)
    repo_path = repo_handler.get_local_path()

    if not repo_path or not os.path.exists(repo_path):
        logger.error(f"❌ Repository path does not exist: '{source}'. Exiting.")
        print(f"❌ Repository path does not exist: '{source}'. Exiting.")  # Ensure visible output
        return

    # Extract repo name from the source
    repo_name = repo_handler.get_repo_name()

    # Fix naming for local directories (avoid "..txt" issue)
    if repo_name in [".", ".."]:
        repo_name = "current_directory"

    # Initialize scanner with repo_name (ensures correct cache handling)
    scanner = Scanner(
        repo_name=repo_name,
        root_path=repo_path,
        include_patterns=include,
        exclude_patterns=exclude,
        size_limit=size_limit
    )

    # Handle force rescan (clears cache for the specific repository)
    if force_rescan:
        cache_file = scanner.cache_file
        if os.path.exists(cache_file):
            os.remove(cache_file)
            logger.info(f"♻️ Cache cleared for {repo_name}. Performing a full rescan.")
            print(f"♻️ Cache cleared for {repo_name}. Performing a full rescan.")  # Ensure visible output

    # Scan repository
    logger.info("🚀 Scanning repository...")
    valid_files = scanner.scan_directory()

    if not valid_files:
        logger.warning("⚠️ No valid files found. Exiting.")
        print("⚠️ No valid files found. Exiting.")
        return

    print(f"✅ Found {len(valid_files)} valid files.")

    # Generate output with OutputBuilder
    logger.info(f"📦 Processing {len(valid_files)} files into {format.upper()} format...")
    output_builder = OutputBuilder(repo_name=repo_name, max_lines=max_lines, output_format=format)
    output_file = output_builder.generate_output(valid_files, repo_path)

    logger.info(f"✅ Output saved to: {output_file}")
    print(f"📄 Output file generated: {output_file}")

if __name__ == "__main__":
    main()
