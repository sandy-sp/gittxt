import click
from rich.console import Console
from pathlib import Path
import subprocess
import shutil

console = Console()

PLUGINS_DIR = Path(__file__).resolve().parent.parent.parent / "plugins"
PLUGIN_LIST = {
    "gittxt-api": {
        "path": PLUGINS_DIR / "gittxt_api",
        "run_cmd": "uvicorn gittxt_api.main:app --reload"
    },
    "gittxt-streamlit": {
        "path": PLUGINS_DIR / "gittxt_streamlit",
        "run_cmd": "streamlit run app.py"
    }
    # Add future plugins here
}

@click.group(help="🔌 Manage optional Gittxt plugins.")
def plugin():
    pass

@plugin.command("list")
def list_plugins():
    console.print("🧙 Available Plugins:\n")
    for name, meta in PLUGIN_LIST.items():
        installed = meta["path"].exists()
        console.print(f"- {name} {'[green](installed)' if installed else '[red](not installed)'}")

@plugin.command("run")
@click.argument("plugin_name")
def run_plugin(plugin_name):
    plugin = PLUGIN_LIST.get(plugin_name)
    if not plugin:
        console.print(f"[red]❌ Unknown plugin: {plugin_name}[/red]")
        return

    if not plugin["path"].exists():
        console.print(f"[red]❌ Plugin '{plugin_name}' is not installed.[/red]")
        return

    # Check for and install dependencies
    req_file = plugin["path"] / "requirements.txt"
    if req_file.exists():
        console.print(f"[cyan]📦 Installing dependencies for {plugin_name}...[/cyan]")
        subprocess.run(["pip", "install", "-r", str(req_file)], cwd=plugin["path"])

    console.print(f"[cyan]🚀 Launching plugin: {plugin_name}[/cyan]")
    subprocess.run(plugin["run_cmd"].split(), cwd=plugin["path"])

@plugin.command("install")
@click.argument("plugin_name")
def install_plugin(plugin_name):
    plugin = PLUGIN_LIST.get(plugin_name)
    if not plugin:
        console.print(f"[red]❌ Unknown plugin: {plugin_name}[/red]")
        return

    if plugin["path"].exists():
        console.print(f"[yellow]⚠️ Plugin '{plugin_name}' is already installed.[/yellow]")
        return

    console.print(f"[green]📦 Installing plugin: {plugin_name}[/green]")
    template_path = Path(__file__).parent.parent.parent / "plugin_templates" / plugin_name
    if not template_path.exists():
        console.print(f"[red]❌ No local template found for: {plugin_name}[/red]")
        return

    shutil.copytree(template_path, plugin["path"])
    console.print(f"[green]✅ Plugin '{plugin_name}' installed at {plugin['path']}[/green]")

@plugin.command("uninstall")
@click.argument("plugin_name")
def uninstall_plugin(plugin_name):
    plugin = PLUGIN_LIST.get(plugin_name)
    if not plugin:
        console.print(f"[red]❌ Unknown plugin: {plugin_name}[/red]")
        return

    if not plugin["path"].exists():
        console.print(f"[yellow]⚠️ Plugin '{plugin_name}' is not installed.[/yellow]")
        return

    confirm = click.confirm(f"🗑️ Are you sure you want to delete {plugin_name}?", default=False)
    if confirm:
        shutil.rmtree(plugin["path"])
        console.print(f"[green]✅ Plugin '{plugin_name}' removed.[/green]")
    else:
        console.print("[cyan]❎ Uninstall canceled.[/cyan]")
