import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from gittxt.utils.filetype_utils import FiletypeConfigManager, is_text_file

console = Console()

@click.group(help="🗂 Manage textual filetype whitelist/blacklist by extension.")
def filetypes():
    pass

@filetypes.command("list", help="🔍 Show current whitelist and blacklist of file extensions.")
def list_types():
    config = FiletypeConfigManager.load_filetype_config()
    table = Table(title="Current Whitelist & Blacklist")
    table.add_column("✅ Whitelist", style="green")
    table.add_column("❌ Blacklist", style="red")

    max_len = max(len(config.get("whitelist", [])), len(config.get("blacklist", [])))
    for i in range(max_len):
        wl = config.get("whitelist", [])[i] if i < len(config.get("whitelist", [])) else ""
        bl = config.get("blacklist", [])[i] if i < len(config.get("blacklist", [])) else ""
        table.add_row(wl, bl)
    console.print(table)

@filetypes.command(help="➕ Add extensions to the textual whitelist.")
@click.argument("exts", nargs=-1)
def whitelist(exts):
    config = FiletypeConfigManager.load_filetype_config()
    for ext in exts:
        normalized_ext = ext.lower() if ext.startswith('.') else f".{ext.lower()}"
        dummy = Path(f"test{normalized_ext}")
        if not is_text_file(dummy):
            console.print(f"[red]❌ `{ext}` is not considered textual by default heuristics. Skipping.")
            continue

        if normalized_ext in config.get("blacklist", []):
            config["blacklist"].remove(normalized_ext)
            console.print(f"[yellow]Removed `{normalized_ext}` from blacklist.")
        if normalized_ext not in config.get("whitelist", []):
            config["whitelist"].append(normalized_ext)
            console.print(f"[green]Added `{normalized_ext}` to whitelist.")

    FiletypeConfigManager.save_filetype_config(config)

@filetypes.command(help="🚫 Add extensions to the non-textual blacklist.")
@click.argument("exts", nargs=-1)
def blacklist(exts):
    config = FiletypeConfigManager.load_filetype_config()
    for ext in exts:
        normalized_ext = ext.lower() if ext.startswith('.') else f".{ext.lower()}"
        # Move from whitelist to blacklist if necessary
        if normalized_ext in config.get("whitelist", []):
            config["whitelist"].remove(normalized_ext)
            console.print(f"[yellow]Removed `{normalized_ext}` from whitelist.")
        if normalized_ext not in config.get("blacklist", []):
            config["blacklist"].append(normalized_ext)
            console.print(f"[red]Added `{normalized_ext}` to blacklist.")
    FiletypeConfigManager.save_filetype_config(config)

@filetypes.command(help="🧹 Clear both whitelist and blacklist.")
def clear():
    FiletypeConfigManager.save_filetype_config({"whitelist": [], "blacklist": []})
    console.print("[cyan]Whitelist and blacklist cleared.")
