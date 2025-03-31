from pathlib import Path
import click
from gittxt.core.config import ConfigManager


def run_interactive_install():
    """
    Simplified interactive install wizard for gittxt-config.json setup,
    focusing only on textual scanning (no subcategory toggles).
    """
    click.echo("\n🎉 Welcome to the Gittxt Interactive Installer 🛠️\n")

    config = ConfigManager.load_config()

    # Output directory
    current_out_dir = config.get("output_dir", "")
    click.echo(f"Current output directory: {current_out_dir}")
    if click.confirm("Would you like to change the output directory?", default=False):
        new_dir = click.prompt(
            "Enter the absolute or relative output directory", default=current_out_dir
        )
        config["output_dir"] = str(Path(new_dir).expanduser().resolve())
        click.echo(f"✅ Updated output_dir to: {config['output_dir']}")

    # Logging level
    logging_choices = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    current_log_level = config.get("logging_level", "INFO")
    click.echo(f"\nCurrent logging level: {current_log_level}")
    new_level = click.prompt(
        "Select logging level",
        type=click.Choice(logging_choices, case_sensitive=False),
        default=current_log_level.upper(),
    )
    config["logging_level"] = new_level.upper()
    click.echo(f"✅ Updated logging_level to: {config['logging_level']}")

    # Output formats
    output_fmt = config.get("output_format", "txt")
    click.echo(f"\nCurrent output format(s): {output_fmt}")
    new_fmt = click.prompt(
        "Enter output formats (comma-separated: txt, json, md)", default=output_fmt
    )
    config["output_format"] = new_fmt
    click.echo(f"✅ Updated output_format to: {config['output_format']}")

    # Optional ZIP
    if click.confirm(
        "Would you like ZIP bundles to be created by default?", default=False
    ):
        config["auto_zip"] = True
    else:
        config["auto_zip"] = False
    click.echo(f"✅ ZIP bundling set to: {config['auto_zip']}")

    ConfigManager.save_config_updates(config)
    click.echo("\n🎉 Setup complete! Your configuration has been saved.\n")

    # Optional filters setup
    if "filters" not in config:
        config["filters"] = {}

    filters = config["filters"]

    if click.confirm("Would you like to configure file filters (extensions/folders)?", default=True):
        # Textual
        current_textual = filters.get("textual_exts", [])
        click.echo(f"Current textual extensions: {', '.join(current_textual) or '-'}")
        new_textual = click.prompt("Enter textual extensions (comma-separated)", default=",".join(current_textual))
        filters["textual_exts"] = sorted(set(e.strip() for e in new_textual.split(",")))

        # Non-Textual
        current_non = filters.get("non_textual_exts", [])
        click.echo(f"Current non-textual extensions: {', '.join(current_non) or '-'}")
        new_non = click.prompt("Enter non-textual extensions (comma-separated)", default=",".join(current_non))
        filters["non_textual_exts"] = sorted(set(e.strip() for e in new_non.split(",")))

        # Excluded Dirs
        current_dirs = filters.get("excluded_dirs", [])
        click.echo(f"Current excluded dirs: {', '.join(current_dirs) or '-'}")
        new_dirs = click.prompt("Enter excluded directories (comma-separated)", default=",".join(current_dirs))
        filters["excluded_dirs"] = sorted(set(e.strip() for e in new_dirs.split(",")))

        ConfigManager.save_config_updates(config)