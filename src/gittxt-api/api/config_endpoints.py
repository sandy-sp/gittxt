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
        config = ConfigManager.load_config()
        # Only expose relevant editable fields
        return {
            "output_dir": config.get("output_dir"),
            "logging_level": config.get("logging_level"),
            "output_format": config.get("output_format"),
            "file_types": config.get("file_types"),
            "auto_zip": config.get("auto_zip")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load config: {e}")


@router.post("/")
def update_config(req: UpdateConfigRequest):
    """
    Update editable parts of Gittxt config.
    """
    try:
        config = ConfigManager.load_config()
        updates = {}

        if req.output_dir:
            config["output_dir"] = req.output_dir
            updates["output_dir"] = req.output_dir

        if req.logging_level:
            config["logging_level"] = req.logging_level.upper()
            updates["logging_level"] = req.logging_level.upper()

        if req.output_format:
            config["output_format"] = req.output_format
            updates["output_format"] = req.output_format

        if req.file_types:
            config["file_types"] = req.file_types
            updates["file_types"] = req.file_types

        if req.auto_zip is not None:
            config["auto_zip"] = req.auto_zip
            updates["auto_zip"] = req.auto_zip

        ConfigManager.save_config_updates(config)

        return {"success": True, "updated_config": updates}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Config update failed: {e}")
