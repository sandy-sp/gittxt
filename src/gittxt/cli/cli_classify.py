import click
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from gittxt.core.logger import Logger
from gittxt.core.repository import RepositoryHandler
from gittxt.utils.filetype_utils import classify_simple, FiletypeConfigManager
from gittxt.utils.pattern_utils import normalize_patterns, match_exclude_dir
from gittxt.utils.repo_url_parser import parse_github_url

logger = Logger.get_logger(__name__)
console = Console()

@click.command("classify", help="🔍 Show summary of file types (Whitelist/Textual vs Blacklist/Non-Textual)")
@click.argument("repo")
@click.option("--exclude-dir", "exclude_dirs", multiple=True, help="Exclude folders (e.g., .git, node_modules)")
def classify(repo, exclude_dirs):
    exclude_dirs = normalize_patterns(list(exclude_dirs))
    whitelist_types = defaultdict(set)
    blacklist_types = defaultdict(set)

    if Path(repo).exists():
        repo_path = Path(repo).resolve()
        repo_name = repo_path.name
        repo_owner = "local"
    else:
        parsed = parse_github_url(repo)
        handler = RepositoryHandler(repo)
        repo_path, subdir, _, _ = handler.get_local_path()
        repo_path = Path(repo_path) / subdir if subdir else Path(repo_path)
        repo_name = parsed.get("repo", "repo")
        repo_owner = parsed.get("owner", "user")

    config = FiletypeConfigManager.load_filetype_config()
    whitelist_cfg = set(config.get("whitelist", []))
    blacklist_cfg = set(config.get("blacklist", []))

    for file in repo_path.rglob("*"):
        if not file.is_file():
            continue
        if match_exclude_dir(file, exclude_dirs):
            continue

        ext = file.suffix.lower() or "(no ext)"
        primary, _ = classify_simple(file)

        if ext in whitelist_cfg:
            whitelist_types[ext].add(file.name)
        elif ext in blacklist_cfg or primary == "NON-TEXTUAL":
            blacklist_types[ext].add(file.name)
        # else: skip showing default/heuristic

    wl_flat = []
    for ext, names in sorted(whitelist_types.items()):
        if ext == "(no ext)":
            wl_flat.extend(sorted(names))
        else:
            wl_flat.append(ext)

    bl_flat = []
    for ext, names in sorted(blacklist_types.items()):
        if ext == "(no ext)":
            bl_flat.extend(sorted(names))
        else:
            bl_flat.append(ext)

    wl_display = ", ".join(wl_flat) or "-"
    bl_display = ", ".join(bl_flat) or "-"

    wl_panel = Panel(
        Text(f"{wl_display}\n\n[Total: {len(wl_flat)}]", style="green"),
        title="✅ Whitelist / Textual",
        expand=True,
        border_style="green"
    )

    bl_panel = Panel(
        Text(f"{bl_display}\n\n[Total: {len(bl_flat)}]", style="red"),
        title="❌ Blacklist / Non-Textual",
        expand=True,
        border_style="red"
    )

    header_text = Text(f"\n📦 File Type Classification Summary for [bold cyan]{repo_owner}/{repo_name}[/bold cyan]\n", style="bold white")

    console.print(header_text)
    console.print(Columns([wl_panel, bl_panel]))
