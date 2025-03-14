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
      web      -> Launch web interface
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
    change_out_dir = click.prompt("Would you like to change it? (y/n)", default="n")
    if change_out_dir.lower().startswith("y"):
        new_dir = click.prompt("Enter the new output directory", default=current_out_dir)
        config["output_dir"] = os.path.abspath(os.path.expanduser(new_dir))
        click.echo(f"✅ Updated output_dir to: {config['output_dir']}")

    # Current logging level
    current_log_level = config.get("logging_level", "INFO")
    click.echo(f"\nCurrent logging level: {current_log_level}")
    new_level = click.prompt("Enter new logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL or skip)", default=current_log_level)
    config["logging_level"] = new_level.upper()
    click.echo(f"✅ Updated logging_level to: {config['logging_level']}")

    # Optional: enable/disable file logging
    enable_file_logging = config.get("enable_file_logging", True)
    click.echo(f"\nFile logging currently enabled: {enable_file_logging}")
    new_file_logging = click.prompt("Enable file logging? (y/n)", default="y" if enable_file_logging else "n")
    config["enable_file_logging"] = True if new_file_logging.lower().startswith("y") else False
    click.echo(f"✅ Updated enable_file_logging to: {config['enable_file_logging']}")

    # Save updates
    ConfigManager.save_config_updates(config)
    click.echo("\n✅ Gittxt config updated successfully!")
    click.echo("Installation / setup complete. You can now run 'gittxt scan' to test.\n")

@cli.command()
@click.option('--port', default=5000, help='Port to run the web interface on')
@click.option('--host', default='127.0.0.1', help='Host to run the web interface on')
def web(port, host):
    """
    Launch the web interface.
    """
    from src.gittxt_ui.app import create_app
    app = create_app()
    app.run(host=host, port=port)

@cli.command()
@click.argument("repos", nargs=-1)  # Allow multiple repositories
@click.option("--include", multiple=True, help="Include only files matching these patterns.")
@click.option("--exclude", multiple=True, help="Exclude files matching these patterns.")
@click.option("--size-limit", type=int, help="Exclude files larger than this size (bytes).")
@click.option("--branch", type=str, help="Manually specify a Git branch (optional override).")
@click.option("--output-dir", type=click.Path(), default=None, help="Override config's output directory.")
@click.option("--output-format", default=None, help="Comma-separated output formats, e.g. 'txt,json,md'. Default from config.")
@click.option("--max-lines", type=int, default=None, help="Limit number of lines per file.")
@click.option("--summary", is_flag=True, help="Show a summary report of scanned files.")
@click.option("--debug", is_flag=True, help="Enable debug mode for verbose logging.")
@click.option("--docs-only", is_flag=True, help="Only extract documentation files (README, docs/, etc.).")
@click.option("--auto-filter", is_flag=True, help="Skip common unwanted/binary files automatically.")
def scan(repos, include, exclude, size_limit, branch, output_dir, output_format,
         max_lines, summary, debug, docs_only, auto_filter):
    """
    Scan one or more repositories (local or remote), extracting text and generating outputs.
    \b
    Examples:
      gittxt scan . --output-format txt,json
      gittxt scan https://github.com/user/repo1 repo2 --docs-only --summary
      gittxt scan https://github.com/user/repo/tree/dev/src/utils
    \b
    If a GitHub URL includes a branch in the path (e.g. '/tree/dev'),
    that branch is automatically detected. Use --branch only if you wish
    to override or if the URL does not specify it.
    """
    if not repos:
        click.echo("❌ No repositories specified. Provide at least one path or URL.")
        sys.exit(1)

    # If --debug flag is set, update the logger level and echo the debug message.
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        msg = "🔍 Debug mode enabled."
        logger.debug(msg)
        click.echo(msg)

    # Determine final output directory (CLI option overrides config)
    final_output_dir = output_dir or config.get("output_dir")

    # Determine final output format(s)
    chosen_format = output_format if output_format else config.get("output_format", "txt")

    # Determine max lines to read per file
    final_max_lines = max_lines if max_lines is not None else config.get("max_lines")

    # Build include and exclude patterns
    include_patterns = list(include) if include else config.get("include_patterns", [])
    exclude_patterns = list(exclude) if exclude else config.get("exclude_patterns", [])

    # Determine size limit
    final_size_limit = size_limit if size_limit else config.get("size_limit")

    # Reuse existing repositories from config
    reuse_existing = config.get("reuse_existing_repos", True)

    all_output_files = []

    for repo_source in repos:
        logger.info(f"🚀 Scanning repository source: {repo_source}")

        # Create a RepositoryHandler.
        # If the user provided --branch, it overrides any branch found in the URL.
        repo_handler = RepositoryHandler(repo_source, branch=branch, reuse_existing=reuse_existing)
        local_repo_path = repo_handler.get_local_path()
        if not local_repo_path:
            logger.error("❌ Failed to access repository. Skipping this repo...")
            continue

        # If the user’s GitHub URL included a sub_path (like '/tree/dev/src/utils'),
        # we can restrict scanning to that subfolder or file.
        scan_target = local_repo_path
        if repo_handler.sub_path:
            scan_target = os.path.join(local_repo_path, repo_handler.sub_path)
            if not os.path.exists(scan_target):
                logger.warning(f"⚠️ Sub-path from URL does not exist locally: {scan_target}")
                logger.warning("    Scanning entire repository instead.")
                scan_target = local_repo_path  # fallback

        # Initialize the Scanner with user-specified filters.
        scanner = Scanner(
            root_path=scan_target,
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

        # Gather summary statistics
        total_size = sum(os.path.getsize(f) for f in valid_files)
        file_types = {os.path.splitext(f)[1] for f in valid_files}
        summary_data = {
            "total_files": len(valid_files),
            "total_size": total_size,
            "file_types": list(file_types)
        }

        # Use the final folder name of local_repo_path as the "repo name"
        repo_name = os.path.basename(os.path.normpath(local_repo_path))

        # Initialize OutputBuilder (supports multiple formats)
        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=final_output_dir,
            max_lines=final_max_lines,
            output_format=chosen_format
        )

        # Generate outputs (txt, json, md, etc.)
        generated_files = builder.generate_output(valid_files, local_repo_path, summary_data)
        all_output_files.extend(generated_files)

        # Print summary if requested
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
        logger.info(f"✅ Completed scanning of {len(repos)} repositories.")
        logger.info(f"   Generated files: {all_output_files}")

def main():
    """
    Entry point so that running `python src/gittxt/cli.py ...` works.
    Typically, you'd install the package and call `gittxt` directly.
    """
    cli()

if __name__ == "__main__":
    main()