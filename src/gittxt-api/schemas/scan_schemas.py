# gittxt-api/schemas/scan_schemas.py
from pydantic import BaseModel
from typing import Optional, List

class TreeRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None

class ScanRequest(BaseModel):
    repo_url: str
    file_types: List[str] = ["code", "docs"]
    output_format: str = "txt,json"
    include_patterns: List[str] = []
    exclude_patterns: List[str] = [".git", "node_modules"]
    size_limit: Optional[int] = None
    branch: Optional[str] = None
    tree_depth: Optional[int] = None 
    create_zip: Optional[bool] = False 
