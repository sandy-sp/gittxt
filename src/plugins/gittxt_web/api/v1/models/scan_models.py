from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ScanRequest(BaseModel):
    repo_path: str = Field(..., example="https://github.com/sandy-sp/gittxt")
    branch: Optional[str] = Field(None, example="main")
    exclude_dirs: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    exclude_patterns: Optional[List[str]] = []
    lite: bool = False
    create_zip: bool = False
    docs_only: bool = False
    sync_ignore: bool = False
    size_limit: Optional[int] = None
    tree_depth: Optional[int] = None
    skip_tree: bool = False

class ScanResponse(BaseModel):
    scan_id: str
    repo_name: str
    num_textual_files: int
    num_non_textual_files: int
    artifact_dir: str
    message: str
    summary: Dict[str, Any] = {}
