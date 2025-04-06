import click
import uvicorn
from rich.console import Console

console = Console()

@click.group(help="Run the Gittxt API server.")
def app():
    pass

@app.command("run")
@click.option("--host", default="127.0.0.1", help="Host to bind the API server.")
@click.option("--port", default=8000, help="Port to run the API server on.")
@click.option("--reload", is_flag=True, default=True, help="Enable auto-reload during development.")
def run_api(host, port, reload):
    """
    Launch the Gittxt FastAPI backend.
    """
    console.print(f"[bold green]🚀 Starting Gittxt API at[/bold green] http://{host}:{port}")
    uvicorn.run(
        "gittxt.api.main:app",
        host=host,
        port=port,
        reload=reload,
    )
