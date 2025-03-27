import click
from .cli_scan import scan
from .cli_filetypes import filetypes
from .cli_install import install, clean
from .cli_utils import config
from gittxt.__init__ import __version__

class CustomGroup(click.Group):
    def __init__(self, *args, **kwargs):
        kwargs["invoke_without_command"] = False
        kwargs["help"] = "[🚀] Gittxt CLI - Extract and classify Git repositories."
        super().__init__(*args, **kwargs)

    def list_commands(self, ctx):
        # Custom order instead of alphabetical
        return ["scan", "install", "filetypes", "clean"]
    
@click.group(cls=CustomGroup)
@click.version_option(version=__version__, prog_name="Gittxt CLI 🛠", hidden=True)
def cli():
    pass

cli.add_command(scan)
cli.add_command(filetypes)
cli.add_command(install)
cli.add_command(clean)
