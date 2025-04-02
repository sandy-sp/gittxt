from pydantic import BaseModel
from typing import List, Optional, Dict

class ScanRequest(BaseModel):
    repo_url: str
    output_format: List[str] = ["txt", "json"]
    zip: bool = True
    lite: bool = True
    branch: Optional[str] = None
    subdir: Optional[str] = None

    # Extra config options
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    size_limit: Optional[int] = None
    tree_depth: Optional[int] = None
    log_level: Optional[str] = None 
    sync: Optional[bool] = False


class ScanResponse(BaseModel):
    message: str
    output_dir: str
    summary: Optional[Dict] = None
    manifest: Optional[Dict] = None
