import uvicorn
import click
from gittxt_web.backend.main import app

@click.group()
def cli(): Ellipsis

@cli.command("run")
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8000, type=int)
@click.option("--reload/--no-reload", default=True)
def run(host, port, reload):
    """Start the API."""
    uvicorn.run(app, host=host, port=port, reload=reload)

if __name__ == "__main__":
    cli()
