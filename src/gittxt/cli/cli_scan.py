import sys
import asyncio
import logging
from pathlib import Path
import click
from rich.console import Console
from gittxt.core.logger import Logger
from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.utils.file_utils import load_gittxtignore
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.filetype_utils import FiletypeConfigManager
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT
from .cli_utils import config
from rich.table import Table
from rich import box
from rich.status import Status
from collections import defaultdict

logger = Logger.get_logger(__name__)
console = Console()


@click.command(help="📦 Scan directories or GitHub repos (textual only).")
@click.argument("repos", nargs=-1)
@click.option(
    "--exclude-dir", "-x", "exclude_dirs", multiple=True, help="Exclude folder paths."
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default=None,
    help="Custom output directory.",
)
@click.option(
    "--output-format", "-f", default="txt", help="Comma-separated: txt, json, md."
)
@click.option(
    "--include-patterns", "-i", multiple=True, help="Glob to include (only textual)."
)
@click.option("--exclude-patterns", "-e", multiple=True, help="Glob to exclude.")
@click.option("--zip", "create_zip", is_flag=True, help="Create a ZIP bundle.")
@click.option(
    "--lite", is_flag=True, help="Generate minimal output instead of full content."
)
@click.option("--sync", is_flag=True, default=False, help="Opt-in to .gitignore usage.")
@click.option("--size-limit", type=int, help="Max file size in bytes.")
@click.option("--branch", type=str, help="Git branch for remote repos.")
@click.option(
    "--tree-depth", type=int, default=None, help="Limit tree output to N levels."
)
@click.option(
    "--log-level",
    type=click.Choice(["debug", "info", "warning", "error"], case_sensitive=False),
    default="warning",
    help="Set log verbosity level.",
)
def scan(
    repos,
    sync,
    exclude_dirs,
    size_limit,
    branch,
    output_dir,
    output_format,
    tree_depth,
    log_level,
    create_zip,
    include_patterns,
    exclude_patterns,
    lite,
):
    log_level = getattr(logging, log_level.upper(), logging.INFO)
    Logger.setup_logger(force_stdout=True)
    logging.getLogger().setLevel(log_level)
    logger.debug(f"🔍 Logging level set to: {log_level}")

    if not repos:
        console.print("[bold red]❌ No repositories specified.[/bold red]")
        sys.exit(1)

    # Warn if --branch used with local path
    if branch:
        for r in repos:
            if Path(r).exists():
                console.print(
                    f"[yellow]⚠️ --branch is ignored for local path: {r}[/yellow]"
                )

    # Validate output formats
    VALID_OUTPUT_FORMATS = {"txt", "json", "md"}
    requested = {fmt.strip() for fmt in output_format.split(",")}
    if not requested.issubset(VALID_OUTPUT_FORMATS):
        console.print(f"[red]Invalid format. Allowed: {VALID_OUTPUT_FORMATS}[/red]")
        sys.exit(1)

    mode = "lite" if lite else "rich"
    final_output_dir = (
        Path(output_dir).resolve()
        if output_dir
        else Path(config.get("output_dir")).resolve()
    )

    asyncio.run(
        _handle_repos(
            repos,
            sync,
            exclude_dirs,
            size_limit,
            branch,
            final_output_dir,
            requested,
            tree_depth,
            create_zip,
            include_patterns,
            exclude_patterns,
            mode,
        )
    )


def print_skipped_files(skipped_files):
    if not skipped_files:
        return

    console.print("\n[bold red]⚠️ Skipped Files Summary[/bold red]")
    reasons = defaultdict(list)
    for path, reason in skipped_files:
        reasons[reason].append(path)
        logger.debug(f"⏭️ Skipped: {path} → {reason}")

    for reason, paths in reasons.items():
        console.print(f"[yellow]- {reason}[/yellow]: {len(paths)} files")


def render_summary_table(
    summary_data: dict, repo_name: str, branch: str = None, subdir: str = None
):
    extra_line = ""
    if branch or subdir:
        parts = []
        if branch:
            parts.append(f"Branch: [bold blue]{branch}[/bold blue]")
        if subdir:
            parts.append(f"Subdir: [bold yellow]{subdir.strip('/')}[/bold yellow]")
        extra_line = " " + " ".join(parts)

    summary_table = Table(
        title=f"📊 Gittxt Summary: {repo_name}\n{extra_line}",
        box=box.ROUNDED,
        border_style="cyan",
    )

    summary_table.add_column("Metric", style="bold magenta")
    summary_table.add_column("Value", justify="right", style="green")

    total_files = summary_data.get("total_files", 0)
    total_size = summary_data.get("formatted", {}).get(
        "total_size", f"{summary_data.get('total_size', 0):,} bytes"
    )
    est_tokens = summary_data.get("formatted", {}).get(
        "estimated_tokens", f"{summary_data.get('estimated_tokens', 0):,}"
    )

    summary_table.add_row("📄 Total Files", str(total_files))
    summary_table.add_row("📦 Total Size", total_size)
    summary_table.add_row("🔢 Estimated Tokens", est_tokens)

    console.print(summary_table)

    breakdown = summary_data.get("file_type_breakdown", {})
    token_data_raw = summary_data.get("tokens_by_type", {})
    token_data_fmt = summary_data.get("formatted", {}).get("tokens_by_type", {})

    if breakdown:
        breakdown_table = Table(
            title="🧩 File Type Breakdown",
            box=box.SIMPLE_HEAVY,
            border_style="blue",
            show_header=True,
            header_style="bold white",
        )
        breakdown_table.add_column("Type", style="yellow", no_wrap=True)
        breakdown_table.add_column("Files", justify="right", style="cyan")
        breakdown_table.add_column("Tokens", justify="right", style="magenta")

        for subcat in sorted(breakdown.keys()):
            files = str(breakdown[subcat])
            tokens = token_data_fmt.get(subcat) or f"{token_data_raw.get(subcat, 0):,}"
            breakdown_table.add_row(subcat, files, tokens)

        console.print(breakdown_table)


async def _handle_repos(
    repos,
    sync,
    exclude_dirs,
    size_limit,
    branch,
    final_output_dir,
    output_formats,
    tree_depth,
    create_zip,
    include_patterns,
    exclude_patterns,
    mode,
):
    for repo_source in repos:
        try:
            await _process_one_repo(
                repo_source,
                sync,
                exclude_dirs,
                size_limit,
                branch,
                final_output_dir,
                output_formats,
                tree_depth,
                create_zip,
                include_patterns,
                exclude_patterns,
                mode,
            )
        except Exception as e:
            logger.error(f"❌ Failed processing {repo_source}: {e}")
            console.print(f"[red]❌ {repo_source} => {e}[/red]")


async def _process_one_repo(
    repo_source,
    sync,
    exclude_dirs,
    size_limit,
    branch,
    final_output_dir,
    output_formats,
    tree_depth,
    create_zip,
    include_patterns,
    exclude_patterns,
    mode,
):
    # Decide local vs. remote
    handler = RepositoryHandler(repo_source, branch=branch)
    with Status(
        "[bold cyan]🔄 Cloning / resolving repo...[/bold cyan]", console=console
    ):
        await handler.resolve()
    repo_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()
    scan_root = Path(repo_path)
    if subdir:
        scan_root = scan_root / subdir

    try:
        # Optionally load .gittxtignore if --sync
        dynamic_ignores = load_gittxtignore(scan_root) if sync else []
        merged_exclude_dirs = list(
            set(exclude_dirs) | set(dynamic_ignores) | set(EXCLUDED_DIRS_DEFAULT)
        )
        # Warn user if --include-patterns has known non-textual extensions
        for pattern in include_patterns:
            ext = Path(pattern).suffix.lower()
            if ext and not FiletypeConfigManager.is_known_textual_ext(ext):
                console.print(
                    f"[yellow]⚠️ Warning: Include pattern '{pattern}' targets non-textual file types. These will be skipped.[/yellow]"
                )

        scanner = Scanner(
            root_path=scan_root,
            exclude_dirs=merged_exclude_dirs,
            size_limit=size_limit,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            progress=True,
            use_ignore_file=sync,
        )
        with Status(
            "[bold cyan]🔍 Scanning repository...[/bold cyan]", console=console
        ):
            textual_files, non_textual_files = await scanner.scan_directory()
        skipped_files = scanner.skipped_files

        if not textual_files:
            console.print("[yellow]⚠️ No valid textual files found.[/yellow]")
            return

        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=final_output_dir,
            output_format=",".join(output_formats),
            repo_url=repo_source if is_remote else None,
            branch=used_branch,
            subdir=subdir,
            mode=mode,
        )
        with Status("[bold cyan]🧩 Formatting output...[/bold cyan]", console=console):
            await builder.generate_output(
                textual_files,
                non_textual_files,
                repo_path,
                create_zip=create_zip,
                tree_depth=tree_depth,
            )

        # Summary
        with Status("[bold cyan]📊 Generating summary...[/bold cyan]", console=console):
            summary_data = await generate_summary(textual_files + non_textual_files)
        render_summary_table(summary_data, repo_name, branch=used_branch, subdir=subdir)
        console.print()
        console.print(
            f"[green]✅ Scan complete for {repo_name}. {len(textual_files)} files processed.[/green]"
        )

        if create_zip:
            formats_display = ["zip"]
        else:
            formats_display = sorted(output_formats)

        console.print(f"[blue]📦 Format(s):[/blue] {', '.join(formats_display)}")
        console.print(f"[blue]📁 Output directory:[/blue] {final_output_dir.resolve()}")

        print_skipped_files(skipped_files)

    finally:
        if is_remote:
            cleanup_temp_folder(Path(repo_path))
