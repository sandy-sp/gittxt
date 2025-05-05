from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any

class ScanRequest(BaseModel):
    repo_url: HttpUrl = Field(
        ...,
        description="HTTPS URL of a public Git repo",
        example="https://github.com/openai/tiktoken",
    )
    branch: str | None = Field(
        default=None,
        description="Branch or tag; default = repo’s default branch",
        example="main",
    )
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
    scan_id: str = Field(example="f8f2f1ce‑1c34‑4b7b‑a6f6‑bcd2a18a9987")
    repo_name: str
    num_textual_files: int
    num_non_textual_files: int
    artifact_dir: str
    message: str
    summary: Dict[str, Any] = {}
