from pydantic import BaseModel, Field
from typing import Optional, List, Literal

class FileInfo(BaseModel):
    path: str
    size: int
    ext: str

class InspectRequest(BaseModel):
    repo_path: str = Field(..., example="https://github.com/user/repo")
    branch: Optional[str] = None
    exclude_dirs: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    exclude_patterns: Optional[List[str]] = []
    max_depth: Optional[int] = 3

class InspectResponse(BaseModel):
    scan_id: str
    repo_name: str
    branch: Optional[str]
    repo_tree: str
    textual_files: List[FileInfo]
    non_textual_files: List[FileInfo]
