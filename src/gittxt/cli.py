import click

@click.command()
@click.argument("source")
def main(source):
    """Gittxt: Scan a Git repo and extract text content."""
    click.echo(f"Scanning repository: {source}")

if __name__ == "__main__":
    main()
