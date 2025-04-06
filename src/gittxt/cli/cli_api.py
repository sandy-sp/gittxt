import click
import uvicorn
from rich.console import Console
from pathlib import Path
import os
from gittxt import OUTPUT_DIR

console = Console()

@click.group(help="Run the Gittxt API server.")
def app():
    pass

@app.command("run")
@click.option("--host", default="127.0.0.1", help="Host to bind the API server.")
@click.option("--port", default=8000, type=int, help="Port to run the API server on.")
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload during development.")
@click.option("--log-level", default="info", 
             type=click.Choice(["debug", "info", "warning", "error"], case_sensitive=False),
             help="Set log verbosity level.")
def run_api(host, port, reload, log_level):
    """
    Launch the Gittxt FastAPI backend.
    """
    from gittxt.core.logger import Logger
    
    # Setup logger with appropriate level
    Logger.override_log_level(log_level)
    
    # Ensure required directories exist
    for dir_path in [OUTPUT_DIR, Path("uploads")]:
        os.makedirs(dir_path, exist_ok=True)
        
    console.print(f"[bold green]🚀 Starting Gittxt API at[/bold green] http://{host}:{port}")
    console.print(f"[blue]📂 Output directory:[/blue] {OUTPUT_DIR}")
    console.print(f"[cyan]⚡ Auto-reload:[/cyan] {'Enabled' if reload else 'Disabled'}")
    console.print(f"[magenta]🔊 Log level:[/magenta] {log_level}")
    
    uvicorn.run(
        "gittxt.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
    )
