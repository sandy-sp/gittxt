from pathlib import Path
import click
from gittxt.config import ConfigManager

def run_interactive_install():
    """
    Interactive install wizard to set up gittxt-config.json.
    """
    config = ConfigManager.load_config()

    click.echo("Welcome to Gittxt Interactive Setup 🛠️")
    click.echo("Let's configure your settings...\n")

    # Output directory setup
    current_out_dir = config.get("output_dir", "")
    click.echo(f"Current output directory: {current_out_dir}")
    if click.confirm("Would you like to change it?", default=False):
        new_dir = click.prompt("Enter the new output directory", default=current_out_dir)
        config["output_dir"] = str(Path(new_dir).expanduser().resolve())
        click.echo(f"✅ Updated output_dir to: {config['output_dir']}")

    # Logging level setup
    current_log_level = config.get("logging_level", "INFO")
    click.echo(f"\nCurrent logging level: {current_log_level}")
    new_level = click.prompt("Enter new logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", default=current_log_level)
    config["logging_level"] = new_level.upper()
    click.echo(f"✅ Updated logging_level to: {config['logging_level']}")

    # File logging toggle
    enable_file_logging = config.get("enable_file_logging", True)
    click.echo(f"\nFile logging currently enabled: {enable_file_logging}")
    if click.confirm("Enable file logging?", default=enable_file_logging):
        config["enable_file_logging"] = True
    else:
        config["enable_file_logging"] = False
    click.echo(f"✅ Updated enable_file_logging to: {config['enable_file_logging']}")

    # Save the updates
    ConfigManager.save_config_updates(config)
    click.echo("\n🎉 Setup complete! Your configuration has been updated.\n")
