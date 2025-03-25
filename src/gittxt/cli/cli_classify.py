import click
from pathlib import Path
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from gittxt.core.logger import Logger
from gittxt.core.repository import RepositoryHandler
from gittxt.utils.filetype_utils import classify_simple, FiletypeConfigManager
from gittxt.utils.pattern_utils import normalize_patterns, match_exclude_dir

logger = Logger.get_logger(__name__)
console = Console()

@click.command("classify", help="🔍 Show unique file types and their classifications (TEXTUAL vs NON-TEXTUAL)")
@click.argument("repo")
@click.option("--exclude-dir", "exclude_dirs", multiple=True, help="Exclude folders (e.g., .git, node_modules)")
def classify(repo, exclude_dirs):
    exclude_dirs = normalize_patterns(list(exclude_dirs))
    filetype_status = defaultdict(set)

    if Path(repo).exists():
        repo_path = Path(repo).resolve()
    else:
        handler = RepositoryHandler(repo)
        repo_path, subdir, _, _ = handler.get_local_path()
        repo_path = Path(repo_path) / subdir if subdir else Path(repo_path)

    config = FiletypeConfigManager.load_filetype_config()
    whitelist = set(config.get("whitelist", []))
    blacklist = set(config.get("blacklist", []))

    for file in repo_path.rglob("*"):
        if not file.is_file():
            continue
        if match_exclude_dir(file, exclude_dirs):
            continue

        ext = file.suffix.lower() or "(no ext)"
        primary, _ = classify_simple(file)

        if ext in whitelist:
            status = "✅ Whitelisted"
        elif ext in blacklist:
            status = "❌ Blacklisted"
        else:
            status = "Auto"

        filetype_status[(ext, primary)].add(status)

    table = Table(title=f"File Type Classification Summary for {repo_path.name}")
    table.add_column("Extension", style="cyan")
    table.add_column("Class", style="magenta")
    table.add_column("Status", style="green")

    for (ext, primary), statuses in sorted(filetype_status.items()):
        table.add_row(ext, primary, ", ".join(statuses))

    console.print(table)
