from fastapi import APIRouter, HTTPException
from pathlib import Path as FilePath

from gittxt.utils.tree_utils import generate_tree
from gittxt.api.schemas.inspect import InspectRequest

router = APIRouter()

@router.post("/inspect")
async def inspect_repo(payload: InspectRequest):
    """
    Generate a lightweight directory tree and basic info from a local repo path.

    Args:
        payload (InspectRequest): Contains repo_path

    Returns:
        dict: repo_name, tree structure, file/folder counts
    """
    try:
        repo_path = FilePath(payload.repo_path)

        if not repo_path.exists() or not repo_path.is_dir():
            raise HTTPException(status_code=400, detail="Invalid repository path.")

        tree = generate_tree(repo_path).build()

        file_count = sum(1 for p in repo_path.rglob("*") if p.is_file())
        dir_count = sum(1 for p in repo_path.rglob("*") if p.is_dir())

        return {
            "repo_name": repo_path.name,
            "tree": tree,
            "file_count": file_count,
            "folder_count": dir_count,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
