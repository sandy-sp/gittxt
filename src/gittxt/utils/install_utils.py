from pathlib import Path
import click
from gittxt.core.config import ConfigManager

def run_interactive_install():
    """
    Enhanced interactive install wizard for gittxt-config.json setup.
    """
    click.echo("\n🎉 Welcome to the Gittxt Interactive Installer 🛠️\n")

    # Load current config
    config = ConfigManager.load_config()

    # Output directory setup
    current_out_dir = config.get("output_dir", "")
    click.echo(f"Current output directory: {current_out_dir}")
    if click.confirm("Would you like to change the output directory?", default=False):
        new_dir = click.prompt(
            "Enter the absolute or relative output directory",
            default=current_out_dir
        )
        config["output_dir"] = str(Path(new_dir).expanduser().resolve())
        click.echo(f"✅ Updated output_dir to: {config['output_dir']}")

    # Logging level setup
    logging_choices = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    current_log_level = config.get("logging_level", "INFO")
    click.echo(f"\nCurrent logging level: {current_log_level}")
    new_level = click.prompt(
        "Select logging level",
        type=click.Choice(logging_choices, case_sensitive=False),
        default=current_log_level.upper()
    )
    config["logging_level"] = new_level.upper()
    click.echo(f"✅ Updated logging_level to: {config['logging_level']}")

    # Output formats setup
    output_fmt = config.get("output_format", "txt")
    click.echo(f"\nCurrent output format(s): {output_fmt}")
    new_fmt = click.prompt(
        "Enter output formats (comma-separated: txt, json, md)",
        default=output_fmt
    )
    config["output_format"] = new_fmt
    click.echo(f"✅ Updated output_format to: {config['output_format']}")

    # Default file types setup
    file_types = config.get("file_types", "code,docs")
    click.echo(f"\nCurrent file types: {file_types}")
    new_types = click.prompt(
        "Enter file types to include (comma-separated: code, docs, csv, image)",
        default=file_types
    )
    config["file_types"] = new_types
    click.echo(f"✅ Updated file_types to: {config['file_types']}")

    # Optional ZIP bundle default
    if click.confirm("Would you like ZIP bundles to be created by default?", default=False):
        config["auto_zip"] = True
    else:
        config["auto_zip"] = False
    click.echo(f"✅ ZIP bundling set to: {config['auto_zip']}")

    # Save config
    ConfigManager.save_config_updates(config)
    click.echo("\n🎉 Setup complete! Your configuration has been saved.\n")
