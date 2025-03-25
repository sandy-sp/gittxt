import click
from .cli_scan import scan
from .cli_filetypes import filetypes
from .cli_install import install, clean
from .cli_classify import classify
from gittxt.__init__ import __version__

@click.group()
@click.version_option(version=__version__, prog_name="Gittxt CLI 🛠", hidden=True)
def cli():
    """[🚀] Gittxt CLI - Extract and classify Git repositories."""
    pass

cli.add_command(scan)
cli.add_command(filetypes)
cli.add_command(install)
cli.add_command(clean)
cli.add_command(classify)
