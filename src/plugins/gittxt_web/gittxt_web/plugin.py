import click
from bottle import Bottle, static_file, request, response
import os

# 1. Import core CLI functions directly:
from gittxt_core.commands import (
    scan as core_scan,
    summary  as core_summary,
    reverse  as core_reverse,
    clean    as core_clean,
    config_list, config_update
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# 2. Define a click group for the web plugin:
@click.group(name="web")
def cli_web_group():
    """Lightweight web interface for gittxt."""
    pass

@cli_web_group.command(name="serve")
@click.option("--host",  default="127.0.0.1", help="Host to bind to")
@click.option("--port",  default=8080,        help="Port to listen on")
def serve(host, port):
    """Run the web UI."""
    app = Bottle()

    # 3. Static assets
    @app.route("/")
    def index():
        return static_file("index.html", root=STATIC_DIR)

    @app.route("/<filename:path>")
    def assets(filename):
        return static_file(filename, root=STATIC_DIR)

    # 4. JSON API endpoints, calling core CLI funcs in‑process:
    @app.post("/api/scan")
    def api_scan():
        payload = request.json or {}
        result  = core_scan(path=payload.get("path", ""), **payload.get("opts", {}))
        response.content_type = "application/json"
        return result

    @app.get("/api/summary/<id>")
    def api_summary(id):
        result = core_summary(id)
        response.content_type = "application/json"
        return result

    # Add more endpoints for reverse, clean, config_list/update...

    # 5. Launch
    app.run(host=host, port=port, reloader=True)

