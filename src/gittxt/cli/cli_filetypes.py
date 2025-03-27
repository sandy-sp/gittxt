import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from gittxt.utils.filetype_utils import FiletypeConfigManager

console = Console()

class FiletypesGroup(click.Group):
    def list_commands(self, ctx):
        return ["list", "add-textual", "add-non-textual", "clear"]
    
@click.group(cls=FiletypesGroup, help="🗂 Manage default textual or non-textual extensions.")
def filetypes():
    pass

@filetypes.command("list", help="🔍 Show current textual vs non-textual extensions.")
def list_types():
    config = FiletypeConfigManager.load_config()
    textual = config.get("textual_exts", [])
    non_textual = config.get("non_textual_exts", [])

    table = Table(title="Current Extensions")
    table.add_column("Textual", style="green")
    table.add_column("Non-Textual", style="red")

    max_len = max(len(textual), len(non_textual))
    for i in range(max_len):
        txt_val = textual[i] if i < len(textual) else ""
        non_val = non_textual[i] if i < len(non_textual) else ""
        table.add_row(txt_val, non_val)

    console.print(table)

@filetypes.command(help="➕ Add extensions to the textual list.")
@click.argument("exts", nargs=-1)
def add_textual(exts):
    all_exts = []
    for raw in exts:
        all_exts.extend([e.strip() for e in raw.split(",") if e.strip()])

    for ext in all_exts:
        normalized = ext if ext.startswith('.') else f".{ext.lower()}"
        FiletypeConfigManager.add_textual_ext(normalized)
        console.print(f"[green]➕ Added '{normalized}' to textual list.")


@filetypes.command(help="🚫 Add extensions to the non-textual list.")
@click.argument("exts", nargs=-1)
def add_non_textual(exts):
    all_exts = []
    for raw in exts:
        all_exts.extend([e.strip() for e in raw.split(",") if e.strip()])
        
    for ext in exts:
        normalized = ext if ext.startswith('.') else f".{ext.lower()}"
        FiletypeConfigManager.add_non_textual_ext(normalized)
        console.print(f"[red]Added '{normalized}' to non-textual list.[/red]")

@filetypes.command(help="🧹 Clear both textual and non-textual extension lists.")
def clear():
    data = {"textual_exts": [], "non_textual_exts": []}
    FiletypeConfigManager.save_config(data)
    console.print("[cyan]Cleared all extension lists.")
