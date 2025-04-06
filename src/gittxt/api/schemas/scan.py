from pydantic import BaseModel
from typing import Optional, List, Dict

class ScanRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None
    subdir: Optional[str] = None
    exclude_dirs: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    exclude_patterns: Optional[List[str]] = []
    size_limit: Optional[int] = None
    tree_depth: Optional[int] = None
    lite: Optional[bool] = False

class DownloadURLs(BaseModel):
    txt: Optional[str] = None
    md: Optional[str] = None
    json: Optional[str] = None
    zip: Optional[str] = None

class ScanResponse(BaseModel):
    scan_id: str
    repo_name: str
    branch: Optional[str]
    summary: Dict
    download_urls: DownloadURLs
