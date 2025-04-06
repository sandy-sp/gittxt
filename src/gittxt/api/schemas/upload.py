from pydantic import BaseModel
from typing import Dict, Optional

class UploadResponse(BaseModel):
    scan_id: str
    repo_name: str
    summary: Dict
    download_urls: Dict[str, Optional[str]]
