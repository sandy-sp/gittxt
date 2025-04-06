import click
from .cli_scan import scan
from gittxt.cli.cli_config import config
from gittxt.cli.cli_utils import clean
from gittxt.cli.cli_reverse import reverse_command
from gittxt.__init__ import __version__


class CustomGroup(click.Group):
    def __init__(self, *args, **kwargs):
        kwargs["invoke_without_command"] = False
        kwargs["help"] = (
            "[📝] Gittxt CLI - Get text from Git repositories in AI-ready formats."
        )
        super().__init__(*args, **kwargs)

    def list_commands(self, ctx):
        # Custom order instead of alphabetical
        return ["scan", "config", "clean", "re"]


@click.group(cls=CustomGroup)
@click.version_option(version=__version__, prog_name="Gittxt CLI 🛠", hidden=True)
def cli():
    pass


cli.add_command(scan)
cli.add_command(config)
cli.add_command(clean)
cli.add_command(reverse_command)
