import click
from rich.console import Console
from rich.table import Table
from gittxt.utils.filetype_utils import FiletypeConfigManager, move_extension

console = Console()

@click.group(help="🗂 Manage filetype whitelist, blacklist, and categories.")
def filetypes():
    pass

@filetypes.command("list", help="🔍 Show current whitelist and blacklist.")
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

@filetypes.command(help="➕ Add extensions to whitelist.")
@click.argument("exts", nargs=-1)
def whitelist(exts):
    config = FiletypeConfigManager.load_filetype_config()
    for ext in exts:
        if ext in config.get("blacklist", []):
            config["blacklist"].remove(ext)
            console.print(f"[yellow]Removed `{ext}` from blacklist.")
        if ext not in config.get("whitelist", []):
            config["whitelist"].append(ext)
            console.print(f"[green]Added `{ext}` to whitelist.")
    FiletypeConfigManager.save_filetype_config(config)

@filetypes.command(help="🚫 Add extensions to blacklist.")
@click.argument("exts", nargs=-1)
def blacklist(exts):
    config = FiletypeConfigManager.load_filetype_config()
    for ext in exts:
        if ext in config.get("whitelist", []):
            config["whitelist"].remove(ext)
            console.print(f"[yellow]Removed `{ext}` from whitelist.")
        if ext not in config.get("blacklist", []):
            config["blacklist"].append(ext)
            console.print(f"[red]Added `{ext}` to blacklist.")
    FiletypeConfigManager.save_filetype_config(config)

@filetypes.command(help="🧹 Clear both whitelist and blacklist.")
def clear():
    FiletypeConfigManager.save_filetype_config({"whitelist": [], "blacklist": []})
    console.print("[cyan]Whitelist and blacklist cleared.")

@filetypes.command("move", help="🔄 Move an extension from one category to another dynamically.")
@click.argument("ext")
@click.argument("from_subcat")
@click.argument("to_subcat")
def move_category(ext, from_subcat, to_subcat):
    from_key = ("TEXTUAL" if from_subcat in ["code", "docs", "configs", "data"] else "NON-TEXTUAL", from_subcat)
    to_key = ("TEXTUAL" if to_subcat in ["code", "docs", "configs", "data"] else "NON-TEXTUAL", to_subcat)
    
    try:
        move_extension(ext, from_key, to_key)
        console.print(f"[green]✅ Moved `{ext}` from `{from_subcat}` to `{to_subcat}` successfully.")
    except Exception as e:
        console.print(f"[red]❌ Failed to move: {e}")
