import click
from gittxt.scanner import Scanner
from gittxt.repository import RepositoryHandler

@click.command()
@click.argument("source")
@click.option("--exclude", multiple=True, help="Exclude files matching this pattern")
@click.option("--size-limit", type=int, help="Exclude files larger than this size (bytes)")
@click.option("--branch", type=str, help="Specify a Git branch (for remote repos)")
def main(source, exclude, size_limit, branch):
    """Gittxt: Scan a Git repo and extract text content."""

    repo_handler = RepositoryHandler(source, branch)
    repo_path = repo_handler.get_local_path()

    if not repo_path:
        click.echo("Failed to access repository. Exiting.")
        return

    scanner = Scanner(root_path=repo_path, exclude_patterns=exclude, size_limit=size_limit)
    valid_files = scanner.scan_directory()

    click.echo(f"Found {len(valid_files)} valid files:")
    for file in valid_files:
        click.echo(f"- {file}")

if __name__ == "__main__":
    main()
