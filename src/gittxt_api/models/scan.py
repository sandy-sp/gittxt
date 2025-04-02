from pydantic import BaseModel, HttpUrl, validator
from typing import List, Optional, Dict, Union
import os

VALID_FORMATS = {"txt", "json", "md", "zip"}

class ScanRequest(BaseModel):
    repo_url: Union[str, HttpUrl]
    output_format: List[str] = ["txt", "json"]
    zip: bool = True
    lite: bool = True
    branch: Optional[str] = None
    subdir: Optional[str] = None

    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    size_limit: Optional[int] = None
    tree_depth: Optional[int] = None
    log_level: Optional[str] = None
    sync: Optional[bool] = False

    @validator("repo_url")
    def validate_repo_url(cls, v):
        if v.startswith(("http://", "https://")):
            return v
        if os.path.exists(v): 
            return v
        raise ValueError("Invalid repo_url: must be a GitHub URL or local path.")

    @validator("output_format", each_item=True)
    def validate_output_format(cls, v):
        if v not in VALID_FORMATS:
            raise ValueError(f"Unsupported output format: {v}")
        return v

class ScanResponse(BaseModel):
    message: str
    output_dir: str
    summary: Optional[Dict] = None
    manifest: Optional[Dict] = None
