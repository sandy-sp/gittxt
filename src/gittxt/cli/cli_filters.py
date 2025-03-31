import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from gittxt.core.config import ConfigManager

console = Console()

FILTER_KEYS = ["textual_exts", "non_textual_exts", "excluded_dirs"]
FILTER_EMOJIS = {
    "textual_exts": "🔠 Textual Extensions",
    "non_textual_exts": "🚫 Non-Textual Extensions",
    "excluded_dirs": "📁 Excluded Directories",
}

@click.group(help="🧩 Manage filters (extensions, excluded folders)")
def filters():
    pass

@filters.command("list", help="🔍 View current textual, non-textual, and excluded folder filters.")
def list_filters():
    config = ConfigManager.load_config()
    filters = config.get("filters", {})

    console.print("[bold cyan]🧩 Current Gittxt Filters[/bold cyan]\n")
    for key in FILTER_KEYS:
        title = FILTER_EMOJIS.get(key, key)
        values = filters.get(key, [])
        if values:
            content = Text(", ".join(sorted(values)), style="green")
        else:
            content = Text("-", style="dim")
        console.print(Panel(content, title=title, expand=False, border_style="blue"))

@filters.command("add", help="➕ Add values to a specific filter category (textual_exts, non_textual_exts, or excluded_dirs).")
@click.argument("filter_type", type=click.Choice(FILTER_KEYS))
@click.argument("values", nargs=-1)
def add_filter(filter_type, values):
    current = set(ConfigManager.get_filter_list(filter_type))
    if filter_type == "textual_exts":
        non_textual = set(ConfigManager.get_filter_list("non_textual_exts"))
        removed = non_textual.intersection(values)
        non_textual.difference_update(values)
        ConfigManager.update_filter_list("non_textual_exts", list(non_textual))
        if removed:
            console.print(f"[yellow]⚠️ Removed from non_textual_exts: {', '.join(sorted(removed))}[/yellow]")
    elif filter_type == "non_textual_exts":
        textual = set(ConfigManager.get_filter_list("textual_exts"))
        conflict = textual.intersection(values)
        if conflict:
            console.print(f"[red]❌ Cannot move from textual to non-textual: {', '.join(conflict)}[/red]")
            return

    current.update(values)
    ConfigManager.update_filter_list(filter_type, list(current))
    console.print(f"[green]✅ Updated {filter_type}[/green]")

@filters.command("remove", help="➖ Remove values from a specific filter category (textual_exts, non_textual_exts, or excluded_dirs).")
@click.argument("filter_type", type=click.Choice(FILTER_KEYS))
@click.argument("values", nargs=-1)
def remove_filter(filter_type, values):
    current = set(ConfigManager.get_filter_list(filter_type))
    current.difference_update(values)
    ConfigManager.update_filter_list(filter_type, list(current))
    console.print(f"[green]✅ Removed from {filter_type}[/green]")
    skipped = set(values) - current
    if skipped:
        console.print(f"[dim]⏭️ Not found in {filter_type}: {', '.join(sorted(skipped))}[/dim]")

@filters.command("clear", help="🗑️ Clear all filters in all categories.")
@click.option("--force", is_flag=True, help="Force clear without prompt.")
def clear_filters(force):
    if not force:
        confirm = input("⚠️ This will clear all filters. Proceed? (y/n): ").strip().lower()
        if confirm != "y":
            console.print("[green]❎ Aborted[/green]")
            return
    for key in FILTER_KEYS:
        ConfigManager.update_filter_list(key, [])
    console.print("[yellow]⚠️ All filters cleared[/yellow]")
