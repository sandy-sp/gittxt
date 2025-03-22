from pydantic import BaseModel
from typing import Optional, List

class TreeRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None

class ScanRequest(BaseModel):
    repo_url: str
    file_types: List[str] = ["code", "docs"]  # Aligned with CLI
    output_format: str = "txt,json"           # Aligned with CLI
    include_patterns: List[str] = []
    exclude_patterns: List[str] = [".git", "node_modules"]
    size_limit: Optional[int] = None
    branch: Optional[str] = None
    tree_depth: Optional[int] = None          # NEW
    create_zip: Optional[bool] = False        # NEW
