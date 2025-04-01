from pydantic import BaseModel, HttpUrl
from typing import List, Literal, Optional, Dict

class ScanRequest(BaseModel):
    repo_url: HttpUrl
    branch: Optional[str] = None
    subdir: Optional[str] = None
    exclude_patterns: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    output_format: List[Literal['txt', 'json', 'md', 'zip']] = ['txt']
    lite: bool = False
    size_limit: Optional[int] = 51200  # 50 KB default

class ScanResponse(BaseModel):
    scan_id: str
    repo_name: Optional[str] = None
    timestamp: Optional[str] = None
    summary: Dict
    directory_tree: str
    file_types: Dict[str, List[str]]
