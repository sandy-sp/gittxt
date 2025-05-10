import click
from bottle import Bottle, static_file, request, response
import os

# Import core CLI functions directly
from gittxt_core.commands import (
    scan as core_scan,
    summary as core_summary,
    reverse as core_reverse,
    clean as core_clean,
    config_list as core_config_list,
    config_update as core_config_update,
)

# Directory for static assets
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@click.group(name="web")
def cli_web_group():
    """Lightweight web interface for gittxt."""
    pass

@cli_web_group.command(name="serve")
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8080, type=int, help="Port to listen on")
def serve(host, port):
    """Run the web UI."""
    app = Bottle()

    # Static HTML and assets
    @app.route("/")
    def index():
        return static_file("index.html", root=STATIC_DIR)

    @app.route("/<filename:path>")
    def assets(filename):
        return static_file(filename, root=STATIC_DIR)

    # JSON API endpoints
    @app.post("/api/scan")
    def api_scan():
        payload = request.json or {}
        result = core_scan(path=payload.get("path", ""), **payload.get("opts", {}))
        response.content_type = "application/json"
        return result

    @app.get("/api/summary/<id>")
    def api_summary(id):
        result = core_summary(id)
        response.content_type = "application/json"
        return result

    @app.post("/api/reverse")
    def api_reverse():
        payload = request.json or {}
        result = core_reverse(path=payload.get("path", ""), **payload.get("opts", {}))
        response.content_type = "application/json"
        return result

    @app.post("/api/clean")
    def api_clean():
        payload = request.json or {}
        result = core_clean(path=payload.get("path", ""))
        response.content_type = "application/json"
        return result

    @app.get("/api/config")
    def api_config_list():
        result = core_config_list()
        response.content_type = "application/json"
        return result

    @app.post("/api/config")
    def api_config_update():
        payload = request.json or {}
        key = payload.get("key")
        value = payload.get("value")
        result = core_config_update(key, value)
        response.content_type = "application/json"
        return result

    # Start the server
    app.run(host=host, port=port, reloader=True)
