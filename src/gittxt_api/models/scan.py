from pydantic import BaseModel, HttpUrl, validator, field_validator
from typing import List, Optional, Dict, Union, Tuple
from pathlib import Path
import os
import uuid

VALID_FORMATS = {"txt", "json", "md", "zip"}

class ScanRequest(BaseModel):
    repo_url: Union[str, HttpUrl]
    output_format: List[str] = ["txt", "json"]
    create_zip: bool = True
    lite_mode: bool = True
    branch: Optional[str] = None
    subdir: Optional[str] = None

    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    size_limit: Optional[int] = None
    tree_depth: Optional[int] = None
    log_level: Optional[str] = None
    sync_ignore: Optional[bool] = True
    exclude_dirs: Optional[List[str]] = None
    output_dir: Optional[str] = f"/tmp/gittxt_output_{uuid.uuid4().hex[:8]}"

    @validator("repo_url")
    def validate_repo_url(cls, v):
        # Allow HTTPS, git@, and local paths
        if isinstance(v, str):
            if v.startswith(("http://", "https://", "git@", "ssh://")) or os.path.exists(v):
                return v
        raise ValueError("Invalid repo_url: must be a GitHub URL, SSH-style git URL, or valid local path.")

    @validator("output_format", each_item=True)
    def validate_output_format(cls, v):
        v = v.lower().strip()
        if v not in VALID_FORMATS:
            raise ValueError(f"Unsupported output format: {v}")
        return v

    @validator("output_dir", pre=True, always=True)
    def normalize_output_dir(cls, v):
        if not v:
            return f"/tmp/gittxt_output_{uuid.uuid4().hex[:8]}"
        return str(Path(v).resolve())


class ScanResponse(BaseModel):
    repo_name: str
    output_dir: str
    output_files: List[str]
    total_files: int
    total_size_bytes: int
    estimated_tokens: int
    file_type_breakdown: Dict[str, int]
    tokens_by_type: Dict[str, int]
    skipped_files: List[Tuple[str, str]]
