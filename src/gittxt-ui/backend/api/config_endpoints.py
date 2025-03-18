# src/gittxt-ui/backend/api/config_endpoints.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from gittxt.config import ConfigManager

router = APIRouter()

class UpdateConfigRequest(BaseModel):
    output_dir: str | None = None
    logging_level: str | None = None
    # Add other config fields you might allow updates for

@router.get("/")
def get_config():
    """
    Return the current Gittxt config so the frontend can see global settings
    like output_dir, file_types, etc.
    """
    return ConfigManager.load_config()

@router.post("/")
def update_config(req: UpdateConfigRequest):
    """
    Update certain Gittxt config fields (like output_dir, logging_level).
    """
    config = ConfigManager.load_config()
    if req.output_dir:
        config["output_dir"] = req.output_dir
    if req.logging_level:
        config["logging_level"] = req.logging_level.upper()

    try:
        ConfigManager.save_config_updates(config)
        return {"success": True, "updated_config": config}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
