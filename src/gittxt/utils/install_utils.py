import click
from pathlib import Path
from gittxt.core.config import ConfigManager
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT, DEFAULT_FILETYPE_CONFIG

DEFAULT_OUTPUT_DIR = Path("gittxt-output").resolve()
DEFAULT_OUTPUT_FORMAT = "txt"


def normalize_extensions(exts):
    """
    Ensure all extensions begin with a '.' and are lowercase.
    """
    return sorted(
        {f".{ext.strip().lstrip('.').lower()}" for ext in exts if ext.strip()}
    )


def run_interactive_install():
    click.echo("🛠️ Welcome to the Gittxt Installer!")
    config = ConfigManager.load_config()

    # === Output Directory ===
    current_output_dir = config.get("output_dir", DEFAULT_OUTPUT_DIR)
    output_dir = click.prompt(
        "📁 Output directory", default=current_output_dir, show_default=True
    )
    config["output_dir"] = output_dir

    # === Output Format ===
    current_format = config.get("output_format", DEFAULT_OUTPUT_FORMAT)
    output_format = click.prompt(
        "📄 Default output format(s) (comma-separated: txt,json,md)",
        default=current_format,
    )
    config["output_format"] = output_format

    # === Logging Level ===
    current_level = config.get("logging_level", "info")
    logging_level = click.prompt(
        "🔊 Logging level (DEBUG/INFO/WARNING/ERROR)",
        type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"], case_sensitive=False),
        default=current_level,
    )
    config["logging_level"] = logging_level

    # === Auto ZIP ===
    auto_zip = click.confirm("🗜️ Enable automatic ZIP bundle creation?", default=True)
    config["auto_zip"] = auto_zip

    # === Filters Block ===
    if "filters" not in config:
        config["filters"] = {}
    filters = config["filters"]

    if click.confirm("🧩 Configure file filters (extensions/folders)?", default=True):
        # --- Textual Extensions ---
        current_textual = filters.get(
            "textual_exts", DEFAULT_FILETYPE_CONFIG["textual_exts"]
        )
        click.echo(f"🔠 Current textual extensions: {', '.join(current_textual)}")
        new_textual = click.prompt(
            "Enter textual extensions (comma-separated)",
            default=",".join(current_textual),
        )
        filters["textual_exts"] = normalize_extensions(new_textual.split(","))

        # --- Non-Textual Extensions ---
        current_nontextual = filters.get(
            "non_textual_exts", DEFAULT_FILETYPE_CONFIG["non_textual_exts"]
        )
        click.echo(
            f"🚫 Current non-textual extensions: {', '.join(current_nontextual)}"
        )
        new_non = click.prompt(
            "Enter non-textual extensions (comma-separated)",
            default=",".join(current_nontextual),
        )
        filters["non_textual_exts"] = normalize_extensions(new_non.split(","))

        # --- Excluded Dirs ---
        current_excluded = filters.get("excluded_dirs", EXCLUDED_DIRS_DEFAULT)
        click.echo(f"📁 Current excluded directories: {', '.join(current_excluded)}")
        new_dirs = click.prompt(
            "Enter excluded directories (comma-separated)",
            default=",".join(current_excluded),
        )
        filters["excluded_dirs"] = sorted(
            {d.strip() for d in new_dirs.split(",") if d.strip()}
        )

    # Save final config
    try:
        ConfigManager.save_config_updates(config)
        click.echo("✅ Configuration saved to gittxt-config.json")
    except Exception as e:
        click.echo(f"❌ Failed to save config: {e}")
        raise click.Abort()
