from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import os
from pathlib import Path

from gittxt.core.logger import Logger
from gittxt.utils.tree_utils import generate_tree

router = APIRouter()
logger = Logger.get_logger(__name__)

@router.get("/inspect")
async def inspect_repository(
    path: str = Query(..., description="Path to the repository to inspect"),
    max_depth: Optional[int] = Query(None, description="Maximum depth for the tree view")
):
    """Inspect a local repository and return its structure"""
    logger.info(f"Inspecting repository at path: {path}")
    
    repo_path = Path(path)
    
    if not repo_path.exists():
        logger.warning(f"Repository path not found: {path}")
        raise HTTPException(status_code=404, detail="Repository path not found")
        
    if not repo_path.is_dir():
        logger.warning(f"Path is not a directory: {path}")
        raise HTTPException(status_code=400, detail="Path must be a directory")
        
    try:
        tree = generate_tree(repo_path, max_depth=max_depth)
        return {"path": str(repo_path), "tree": tree}
    except Exception as e:
        logger.error(f"Failed to inspect repository: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to inspect repository: {str(e)}"
        )
