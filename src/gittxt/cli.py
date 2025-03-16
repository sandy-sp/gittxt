from pathlib import Path
import click
import sys
import logging

from gittxt.config import ConfigManager
from gittxt.logger import Logger
from gittxt.scanner import Scanner
from gittxt.repository import RepositoryHandler
from gittxt.output_builder import OutputBuilder

logger = Logger.get_logger(__name__)

# Load configuration once
config = ConfigManager.load_config()

@click.group()
def cli():
    """Gittxt v1.3.1 CLI
        Subcommands:
            install  -> Interactive config setup
            scan     -> Scan one or more repositories"""
    pass

@cli.command()
def install():
    """Interactive install command that updates gittxt-config.json"""
    click.echo("Welcome to Gittxt v2.0.0 interactive setup!")
    click.echo("We'll update your local gittxt-config.json...")

    # Output directory
    current_out_dir = config.get("output_dir", "")
    click.echo(f"\nCurrent default output directory: {current_out_dir}")
    change_out_dir = click.prompt("Would you like to change it? (y/n)", default="n")
    if change_out_dir.lower().startswith("y"):
        new_dir = click.prompt("Enter the new output directory", default=current_out_dir)
        config["output_dir"] = str(Path(new_dir).expanduser().resolve())
        click.echo(f"✅ Updated output_dir to: {config['output_dir']}")

    # Logging level
    current_log_level = config.get("logging_level", "INFO")
    click.echo(f"\nCurrent logging level: {current_log_level}")
    new_level = click.prompt("Enter new logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL or skip)", default=current_log_level)
    config["logging_level"] = new_level.upper()
    click.echo(f"✅ Updated logging_level to: {config['logging_level']}")

    # File logging toggle
    enable_file_logging = config.get("enable_file_logging", True)
    click.echo(f"\nFile logging currently enabled: {enable_file_logging}")
    new_file_logging = click.prompt("Enable file logging? (y/n)", default="y" if enable_file_logging else "n")
    config["enable_file_logging"] = True if new_file_logging.lower().startswith("y") else False
    click.echo(f"✅ Updated enable_file_logging to: {config['enable_file_logging']}")

    ConfigManager.save_config_updates(config)
    click.echo("\n✅ Gittxt config updated successfully!")
    click.echo("Installation / setup complete. You can now run 'gittxt scan' to test.\n")

@cli.command()
@click.argument("repos", nargs=-1)
@click.option("--include", multiple=True)
@click.option("--exclude", multiple=True)
@click.option("--size-limit", type=int)
@click.option("--branch", type=str)
@click.option("--output-dir", type=click.Path(), default=None)
@click.option("--output-format", default=None)
@click.option("--max-lines", type=int, default=None)
@click.option("--summary", is_flag=True)
@click.option("--debug", is_flag=True)
@click.option("--docs-only", is_flag=True)
@click.option("--auto-filter", is_flag=True)
def scan(repos, include, exclude, size_limit, branch, output_dir, output_format,
         max_lines, summary, debug, docs_only, auto_filter):
    """Scan one or more repositories (local or remote)"""

    if not repos:
        click.echo("❌ No repositories specified. Provide at least one path or URL.")
        sys.exit(1)

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Debug mode enabled.")
        click.echo("🔍 Debug mode enabled.")

    final_output_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    chosen_format = output_format if output_format else config.get("output_format", "txt")
    final_max_lines = max_lines if max_lines is not None else config.get("max_lines")
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

        total_size = sum(Path(f).stat().st_size for f in valid_files)
        file_types = {Path(f).suffix for f in valid_files}
        summary_data = {
            "total_files": len(valid_files),
            "total_size": total_size,
            "file_types": list(file_types)
        }

        repo_name = Path(repo_path).name

        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=final_output_dir,
            max_lines=final_max_lines,
            output_format=chosen_format
        )

        generated_files = builder.generate_output(valid_files, repo_path, summary_data)
        all_output_files.extend(generated_files)

        if summary:
            logger.info("📊 Summary Report:")
            logger.info(f" - Scanned {summary_data['total_files']} text files")
            logger.info(f" - Total Size: {summary_data['total_size']} bytes")
            logger.info(f" - File Types: {', '.join(summary_data['file_types'])}")
            if "estimated_tokens" in summary_data:
                logger.info(f" - Estimated Tokens: {summary_data['estimated_tokens']}")
            for out_f in generated_files:
                logger.info(f" - Output Saved: {out_f}")

    if not all_output_files:
        click.echo("❌ No outputs were generated. Verify your repository or filtering options.")
    else:
        logger.info(f"✅ Completed scanning of {len(repos)} repositories. Output files: {all_output_files}")

def main():
    cli()

if __name__ == "__main__":
    main()
