import click
import uvicorn
from rich.console import Console
from pathlib import Path
import os
from gittxt.__init__ import OUTPUT_DIR

console = Console()

@click.group(help="Run the Gittxt API server.")
def app():
    pass

@app.command("run")
@click.option("--host", default="127.0.0.1", help="Host to bind the API server.")
@click.option("--port", default=8000, type=int, help="Port to run the API server on.")
@click.option("--reload", is_flag=True, default=False, help="Enable auto-reload during development.")
def run_api(host, port, reload):
    """
    Launch the Gittxt FastAPI backend.
    """
    # Ensure required directories exist
    for dir_path in [OUTPUT_DIR, Path("uploads")]:
        os.makedirs(dir_path, exist_ok=True)
        
    console.print(f"[bold green]🚀 Starting Gittxt API at[/bold green] http://{host}:{port}")
    console.print(f"[blue]📂 Output directory:[/blue] {OUTPUT_DIR}")
    console.print(f"[cyan]⚡ Auto-reload:[/cyan] {'Enabled' if reload else 'Disabled'}")
    
    uvicorn.run(
        "gittxt.api.main:app",
        host=host,
        port=port,
        reload=reload,
    )
