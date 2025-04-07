from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from pathlib import Path
from os import path

from gittxt.core.logger import Logger
from gittxt.utils.tree_utils import generate_tree
from gittxt.api.schemas.inspect import InspectRequest  # Ensure schema is imported

router = APIRouter()
logger = Logger.get_logger(__name__)

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
        tree, file_count, folder_count = generate_tree(repo_path, max_depth=max_depth, count_items=True)
        return {
            "repo_name": path.basename(repo_path),
            "path": str(repo_path),
            "tree": tree,
            "file_count": file_count,
            "folder_count": folder_count,
        }
    except Exception as e:
        logger.error(f"Failed to inspect repository: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to inspect repository: {str(e)}"
        )
