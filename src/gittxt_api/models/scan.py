from pydantic import BaseModel
from typing import List, Optional, Dict

class ScanRequest(BaseModel):
    repo_url: str
    output_format: List[str] = ["txt", "json"]
    zip: bool = True
    lite: bool = True
    branch: Optional[str] = None

class ScanResponse(BaseModel):
    message: str
    output_dir: str
    summary: Optional[Dict] = None
    manifest: Optional[Dict] = None
