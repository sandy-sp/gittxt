import click
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
@click.option("--output", type=str, default="gittxt_output.txt", help="Specify output file name")
@click.option("--max-lines", type=int, help="Limit number of lines per file")
def main(source, include, exclude, size_limit, branch, output, max_lines):
    """Gittxt: Scan a Git repo and extract text content."""

    logger.info(f"Starting Gittxt on: {source}")

    repo_handler = RepositoryHandler(source, branch)
    repo_path = repo_handler.get_local_path()

    if not repo_path:
        logger.error("Failed to access repository. Exiting.")
        return

    scanner = Scanner(root_path=repo_path, include_patterns=include, exclude_patterns=exclude, size_limit=size_limit)
    valid_files = scanner.scan_directory()

    if not valid_files:
        logger.warning("No valid files found. Exiting.")
        return

    logger.info(f"Processing {len(valid_files)} files...")

    output_builder = OutputBuilder(output_file=output, max_lines=max_lines)
    output_file = output_builder.generate_output(valid_files)

    logger.info(f"✅ Output saved to: {output_file}")

if __name__ == "__main__":
    main()
