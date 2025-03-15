import click
import os
import sys
import logging
from gittxt.config import ConfigManager
from gittxt.logger import Logger
from gittxt.scanner import Scanner
from gittxt.repository import RepositoryHandler
from gittxt.output_builder import OutputBuilder

logger = Logger.get_logger(__name__)

# Load configuration once; CLI options may override these.
config = ConfigManager.load_config()

@click.group()
def cli():
    """
    Gittxt v2.0.0 CLI

    Subcommands:
      install  -> Interactive config setup
      scan     -> Scan one or more repositories
    """
    pass

@cli.command()
def install():
    """
    Interactive install command that prompts the user for key config options
    and saves them into gittxt-config.json.
    """
    click.echo("Welcome to Gittxt v2.0.0 interactive setup!")
    click.echo("We'll update your local gittxt-config.json...")

    # Current output directory
    current_out_dir = config.get("output_dir", "")
    click.echo(f"\nCurrent default output directory: {current_out_dir}")
    change_out_dir = click.confirm("Would you like to change it?", default=False)
    if change_out_dir:
        new_dir = click.prompt("Enter the new output directory", default=current_out_dir)
        config["output_dir"] = os.path.abspath(os.path.expanduser(new_dir))
        click.echo(f"✅ Updated output_dir to: {config['output_dir']}")

    # Current logging level
    current_log_level = config.get("logging_level", "INFO")
    click.echo(f"\nCurrent logging level: {current_log_level}")
    new_level = click.prompt("Enter new logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL or skip)", default=current_log_level)
    config["logging_level"] = new_level.upper()
    click.echo(f"✅ Updated logging_level to: {config['logging_level']}")

    # Enable/disable verbose mode
    verbose_mode = config.get("verbose", False)
    click.echo(f"\nVerbose mode currently {'enabled' if verbose_mode else 'disabled'}")
    config["verbose"] = click.confirm("Enable verbose logging mode?", default=verbose_mode)

    # Save updates
    ConfigManager.save_config_updates(config)
    click.echo("\n✅ Gittxt config updated successfully!")
    click.echo("Installation / setup complete. You can now run 'gittxt scan' to test.\n")

@cli.command()
@click.argument("repos", nargs=-1)
@click.option("--include", multiple=True, help="Include only files matching these patterns.")
@click.option("--exclude", multiple=True, help="Exclude files matching these patterns.")
@click.option("--size-limit", type=int, help="Exclude files larger than this size (bytes).")
@click.option("--branch", type=str, help="Specify a Git branch (for remote repos).")
@click.option("--output-dir", type=click.Path(), default=None, help="Override config's output directory.")
@click.option("--output-format", default=None, help="Comma-separated output formats, e.g. 'txt,json,md'. Default from config.")
@click.option("--summary", is_flag=True, help="Show a summary report of scanned files.")
@click.option("--debug", is_flag=True, help="Enable debug mode for verbose logging.")
@click.option("--docs-only", is_flag=True, help="Only extract documentation files (README, docs/, etc.).")
@click.option("--auto-filter", is_flag=True, help="Skip common unwanted/binary files automatically.")
def scan(repos, include, exclude, size_limit, branch, output_dir, output_format, summary, debug, docs_only, auto_filter):
    """
    Scan one or more repositories (local or remote), extracting text and generating outputs.
    """
    if not repos:
        click.echo("❌ No repositories specified. Provide at least one path or URL.")
        sys.exit(1)

    # If --debug flag is set, update the logger level and echo the expected debug message.
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Debug mode enabled.")
        click.echo("🔍 Debug mode enabled.")

    final_output_dir = output_dir or config.get("output_dir")
    chosen_format = output_format if output_format else config.get("output_format", "txt")
    include_patterns = list(include) if include else config.get("include_patterns", [])
    exclude_patterns = list(exclude) if exclude else config.get("exclude_patterns", [])
    final_size_limit = size_limit if size_limit else config.get("size_limit")
    reuse_existing = config.get("reuse_existing_repos", True)

    all_output_files = []

    for repo_source in repos:
        logger.info(f"🚀 Scanning repository source: {repo_source}")
        repo_handler = RepositoryHandler(repo_source, branch=branch, reuse_existing=reuse_existing)
        repo_path = repo_handler.get_local_path()
        if not repo_path:
            logger.error("❌ Failed to access repository. Skipping this repo...")
            continue

        scanner = Scanner(
            root_path=repo_path,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            size_limit=final_size_limit,
            docs_only=docs_only,
            auto_filter=auto_filter
        )
        valid_files, tree_summary = scanner.scan_directory()
        if not valid_files:
            logger.warning("⚠️ No valid files found for extraction in this repo.")
            continue

        logger.info(f"✅ Processing {len(valid_files)} text files from {repo_source}...")

        total_size = sum(os.path.getsize(f) for f in valid_files)
        file_types = {os.path.splitext(f)[1] for f in valid_files}
        summary_data = {
            "total_files": len(valid_files),
            "total_size": total_size,
            "file_types": list(file_types)
        }

        builder = OutputBuilder(repo_source, output_dir=final_output_dir, output_format=chosen_format)
        generated_files = builder.generate_output(valid_files, repo_path, summary_data)
        all_output_files.extend(generated_files)

    if not all_output_files:
        click.echo("❌ No outputs were generated. Verify your repository or filtering options.")
    else:
        logger.info(f"✅ Completed scanning of {len(repos)} repositories. Output files: {all_output_files}")

if __name__ == "__main__":
    cli()
