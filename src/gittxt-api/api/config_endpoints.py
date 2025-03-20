# gittxt-api/api/config_endpoints.py

from fastapi import APIRouter, HTTPException
from schemas.config_schemas import UpdateConfigRequest
from gittxt.config import ConfigManager

router = APIRouter()

@router.get("/")
def get_config():
    """
    Return the current Gittxt config.
    """
    try:
        return ConfigManager.load_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load config: {e}")


@router.post("/")
def update_config(req: UpdateConfigRequest):
    """
    Update editable parts of Gittxt config (e.g., output_dir, logging_level).
    """
    try:
        config = ConfigManager.load_config()
        if req.output_dir:
            config["output_dir"] = req.output_dir
        if req.logging_level:
            config["logging_level"] = req.logging_level.upper()

        ConfigManager.save_config_updates(config)

        return {"success": True, "updated_config": config}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Config update failed: {e}")
