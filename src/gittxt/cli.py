from pathlib import Path
import click
import sys
import logging
import asyncio
from gittxt import __version__
from gittxt.config import ConfigManager
from gittxt.logger import Logger
from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder, cleanup_old_outputs
from gittxt.utils.filetype_utils import FiletypeConfigManager
from gittxt.utils.summary_utils import generate_summary

logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

@click.group()
@click.version_option(version=__version__, prog_name="Gittxt CLI")
def cli():
    """Gittxt CLI: Scan and extract text/code from GitHub repositories."""
    pass

@cli.command()
def install():
    from gittxt.utils.install_utils import run_interactive_install
    run_interactive_install()

@cli.group()
def filetypes():
    """Manage filetype whitelist and blacklist"""
    pass

@filetypes.command("list")
def list_types():
    """Show current whitelist and blacklist."""
    config = FiletypeConfigManager.load_filetype_config()
    click.echo("📄 Whitelist:")
    for ext in sorted(config.get("whitelist", [])):
        click.echo(f" - {ext}")
    click.echo("\n🚫 Blacklist:")
    for ext in sorted(config.get("blacklist", [])):
        click.echo(f" - {ext}")

@filetypes.command()
@click.argument("exts", nargs=-1)
def whitelist(exts):
    """Add one or more extensions to whitelist."""
    config = FiletypeConfigManager.load_filetype_config()
    for ext in exts:
        if ext in config.get("blacklist", []):
            config["blacklist"].remove(ext)
            click.echo(f"⚠️ Removed `{ext}` from blacklist.")
        if ext not in config.get("whitelist", []):
            config["whitelist"].append(ext)
            click.echo(f"✅ Added `{ext}` to whitelist.")
    FiletypeConfigManager.save_filetype_config(config)

@filetypes.command()
@click.argument("exts", nargs=-1)
def blacklist(exts):
    """Add one or more extensions to blacklist."""
    config = FiletypeConfigManager.load_filetype_config()
    for ext in exts:
        if ext in config.get("whitelist", []):
            config["whitelist"].remove(ext)
            click.echo(f"⚠️ Removed `{ext}` from whitelist.")
        if ext not in config.get("blacklist", []):
            config["blacklist"].append(ext)
            click.echo(f"✅ Added `{ext}` to blacklist.")
    FiletypeConfigManager.save_filetype_config(config)

@filetypes.command()
def clear():
    """Clear whitelist and blacklist."""
    config = {
        "whitelist": [],
        "blacklist": []
    }
    FiletypeConfigManager.save_filetype_config(config)
    click.echo("🧹 Whitelist and blacklist cleared.")

@cli.command()
@click.option("--output-dir", "-o", type=click.Path(), default=None)
def clean(output_dir):
    """Delete old outputs (text/json/md/zips folders)."""
    target_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    cleanup_old_outputs(target_dir)
    click.echo(f"🗑️ Cleaned output directory: {target_dir}")

@cli.command()
@click.argument("repos", nargs=-1)
@click.option("--include", "-i", multiple=True, help="Include files matching patterns (e.g., .py)")
@click.option("--exclude", "-e", multiple=True, help="Exclude files matching patterns (e.g., node_modules)")
@click.option("--size-limit", type=int, help="Maximum file size in bytes")
@click.option("--branch", type=str, help="Specify Git branch to scan")
@click.option("--output-dir", "-o", type=click.Path(), default=None)
@click.option("--output-format", "-f", default="txt,json", help="txt, json, md, or comma-separated list")  # synced with docs
@click.option("--summary", is_flag=True, help="Show summary report after scan")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--progress", is_flag=True, help="Show scan progress bar")
@click.option("--non-interactive", is_flag=True, help="Skip prompts (CI/CD friendly)")
@click.option("--tree-depth", type=int, default=None, help="Limit tree view to N folder levels.")
@click.option("--zip", "create_zip", is_flag=True, help="Generate ZIP bundle with outputs + assets (CI-friendly)")
@click.option("--file-types", default="code,docs", help="Specify types: code, docs, csv, image, media, all")
def scan(
    repos,
    include,
    exclude,
    size_limit,
    branch,
    output_dir,
    output_format,
    summary,
    debug,
    progress,
    non_interactive,
    tree_depth,
    create_zip,
    file_types
):
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("🔍 Debug mode enabled.")

    if not repos:
        logger.error("❌ No repositories specified.")
        raise click.UsageError("❌ No repositories specified. Provide at least one repo URL or path.")

    final_output_dir = Path(output_dir).resolve() if output_dir else Path(config.get("output_dir")).resolve()
    include_patterns = list(include) if include else []
    exclude_patterns = list(exclude) if exclude else config.get("exclude_patterns", [])
    file_types_list = [ft.strip() for ft in file_types.split(",")]

    VALID_FILETYPES = {"code", "docs", "csv", "image", "media", "all"}
    for ft in file_types_list:
        if ft not in VALID_FILETYPES:
            logger.error(f"❌ Invalid file type: {ft}. Valid options: {', '.join(VALID_FILETYPES)}")
            sys.exit(1)

    logger.info(f"🧹 Applying exclude filters: {exclude_patterns or 'None'}")

    for repo_source in repos:
        _process_repo(
            repo_source, branch, include_patterns, exclude_patterns, size_limit,
            final_output_dir, output_format, summary, debug, progress, non_interactive, tree_depth, create_zip, file_types_list
        )

def _process_repo(
    repo_source, branch, include_patterns, exclude_patterns, size_limit,
    final_output_dir, output_format, summary, debug, progress, non_interactive, tree_depth, create_zip, file_types
):
    logger.info(f"🚀 Processing repository: {repo_source}")
    repo_handler = RepositoryHandler(repo_source, branch=branch)
    repo_path, subdir, is_remote, repo_name = repo_handler.get_local_path()

    scan_root = Path(repo_path) / subdir if subdir else Path(repo_path)

    repo_url = None
    if is_remote:
        repo_url = repo_source.split(".git")[0] if ".git" in repo_source else repo_source

    scanner = Scanner(
        root_path=scan_root,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        size_limit=size_limit,
        file_types=file_types,
        progress=progress,
    )

    all_files = scanner.scan_directory()

    if not all_files:
        logger.warning("⚠️ No valid files found. Skipping...")
        if is_remote:
            cleanup_temp_folder(Path(repo_path))
        return

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=final_output_dir,
        output_format=output_format,
        repo_url=repo_url
    )

    if not non_interactive:
        final_zip = click.confirm("📦 Do you want to generate a ZIP bundle with outputs + assets?", default=create_zip)
    else:
        final_zip = create_zip
    
    logger.info(f"ZIP bundling: {'auto' if create_zip else 'manual'} | Interactive: {not non_interactive}")

    asyncio.run(builder.generate_output(all_files, repo_path, create_zip=final_zip, tree_depth=tree_depth))

    if summary:
        summary_data = generate_summary(all_files)
        logger.info("📊 Summary Report:")
        logger.info(f" - Total files: {summary_data.get('total_files')}")
        logger.info(f" - Total size (bytes): {summary_data.get('total_size')}")
        logger.info(f" - Estimated tokens: {summary_data.get('estimated_tokens')}")
        logger.info(f" - File type breakdown: {summary_data.get('file_type_breakdown')}")
        logger.info(f" - Output formats: {output_format}")

        # NEW: always print summary to stdout as well
        click.echo("=== Summary Report ===")
        click.echo(f"Total Files: {summary_data.get('total_files')}")
        click.echo(f"Total Size: {summary_data.get('total_size')} bytes")
        click.echo(f"Estimated Tokens: {summary_data.get('estimated_tokens')}")
        click.echo(f"Output Formats: {output_format}")

    if is_remote:
        cleanup_temp_folder(Path(repo_path))

    logger.info("✅ Gittxt scan completed.\n")

def main():
    cli()

if __name__ == "__main__":
    main()
