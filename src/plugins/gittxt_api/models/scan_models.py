from pydantic import BaseModel
from typing import Optional, List

class ScanRequest(BaseModel):
    repo_path: str
    branch: Optional[str] = None
    exclude_dirs: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    exclude_patterns: Optional[List[str]] = []
    lite: bool = False
    create_zip: bool = False

class ScanResponse(BaseModel):
    scan_id: str
    repo_name: str
    num_textual_files: int
    num_non_textual_files: int
    artifact_dir: str
    message: str
