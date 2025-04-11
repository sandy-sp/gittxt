import click
import uvicorn
from rich.console import Console
from pathlib import Path
import os

from gittxt.core.logger import Logger
from gittxt import OUTPUT_DIR

console = Console()

@click.group(help="Run the Gittxt API plugin (FastAPI server).")
def api_plugin():
    pass

@api_plugin.command("run")
@click.option("--host", default="127.0.0.1", help="Host to bind the API server.")
@click.option("--port", default=8000, type=int, help="Port to run the API server on.")
@click.option("--reload", is_flag=True, default=True, help="Enable auto-reload.")
@click.option("--log-level", default="info", help="Log level.")
def run_api(host, port, reload, log_level):
    Logger.override_log_level(log_level)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    console.print(f"[green]🚀 Starting API at:[/green] http://{host}:{port}")
    uvicorn.run("plugins.gittxt_api.main:app", host=host, port=port, reload=reload, log_level=log_level)

if __name__ == "__main__":
    api_plugin()
