import click
from gittxt.scanner import Scanner

@click.command()
@click.argument("source")
@click.option("--exclude", multiple=True, help="Exclude files matching this pattern")
@click.option("--size-limit", type=int, help="Exclude files larger than this size (bytes)")
def main(source, exclude, size_limit):
    """Gittxt: Scan a Git repo and extract text content."""
    
    scanner = Scanner(root_path=source, exclude_patterns=exclude, size_limit=size_limit)
    valid_files = scanner.scan_directory()

    click.echo(f"Found {len(valid_files)} valid files:")
    for file in valid_files:
        click.echo(f"- {file}")

if __name__ == "__main__":
    main()
