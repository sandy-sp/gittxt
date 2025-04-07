from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from pathlib import Path
from os import path

from gittxt import OUTPUT_DIR  # Ensure consistent output directory
from gittxt.core.config import ConfigManager
from gittxt.core.logger import Logger
from gittxt.utils.tree_utils import generate_tree
from gittxt.api.schemas.inspect import InspectRequest  # Ensure schema is imported

# Load the config once at the top of the file
config = ConfigManager.load_config()

router = APIRouter()
logger = Logger.get_logger(__name__)

# Define unified paths based on config or defaults
UPLOAD_DIR = Path(config.get("upload_dir", OUTPUT_DIR / "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

@router.post("/inspect")  # Changed from @router.get to @router.post
async def inspect_repository(
    request: InspectRequest,  # Accept request body
    max_depth: Optional[int] = Query(None, description="Maximum depth for the tree view")
):
    """Inspect a local repository and return its structure"""
    logger.info(f"Inspecting repository at path: {request.repo_path}")
    
    repo_path = Path(request.repo_path)
    
    if not repo_path.exists():
        logger.warning(f"Repository path not found: {request.repo_path}")
        raise HTTPException(status_code=404, detail="Repository path not found")
        
    if not repo_path.is_dir():
        logger.warning(f"Path is not a directory: {request.repo_path}")
        raise HTTPException(status_code=400, detail="Path must be a directory")
        
    try:
        # Simplified to handle single return value from generate_tree
        tree = generate_tree(repo_path, max_depth=max_depth)
        return {
            "repo_name": path.basename(repo_path),
            "path": str(repo_path),
            "tree": tree,
        }
    except Exception as e:
        logger.error(f"Failed to inspect repository: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to inspect repository: {str(e)}"
        )
