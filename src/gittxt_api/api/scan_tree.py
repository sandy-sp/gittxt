from fastapi import APIRouter, HTTPException, Query
from pathlib import Path

router = APIRouter()


@router.get("/tree")
def get_directory_tree(
    output_dir: str = Query(..., description="Path to scan output directory")
):
    base_path = Path(output_dir)
    if not base_path.exists():
        raise HTTPException(status_code=404, detail="Output directory not found")

    def build_tree(path: Path):
        children = []
        for p in sorted(path.iterdir()):
            if p.is_dir() and not p.name.startswith("."):
                children.append(
                    {
                        "name": p.name,
                        "path": str(p.relative_to(base_path)),
                        "children": build_tree(p),
                    }
                )
        return children

    return {"root": str(base_path.name), "tree": build_tree(base_path)}
