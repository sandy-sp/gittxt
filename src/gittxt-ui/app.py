from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from src.gittxt_ui.routes import router

app = FastAPI()

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="src/gittxt_ui/static"), name="static")

# Load Jinja2 templates
templates = Environment(loader=FileSystemLoader("src/gittxt_ui/templates"))

# Include the API routes
app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Serve the main HTML page."""
    template = templates.get_template("index.html")
    return HTMLResponse(content=template.render(), status_code=200)
