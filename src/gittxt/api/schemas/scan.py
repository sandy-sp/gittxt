from pydantic import BaseModel
from typing import Optional, List, Dict

class ScanRequest(BaseModel):
    repo_path: str
    lite: bool = False

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
