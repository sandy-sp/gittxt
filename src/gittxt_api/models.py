from pydantic import BaseModel, HttpUrl, Field, constr
from typing import List, Literal, Optional, Dict

class ScanRequest(BaseModel):
    repo_url: HttpUrl  # Validates that the URL is properly formatted
    branch: Optional[str] = Field(
        default=None,
        pattern=r"^[a-zA-Z0-9._-]+$",  # Only allow valid branch names
        description="Branch name must be alphanumeric with optional '.', '_', or '-'."
    )
    subdir: Optional[constr(pattern=r"^[a-zA-Z0-9_\-/]*$")] = None  # Allow only valid relative paths
    exclude_patterns: Optional[List[str]] = Field(default_factory=list)
    include_patterns: Optional[List[str]] = Field(default_factory=list)
    output_format: List[Literal['txt', 'json', 'md', 'zip']] = ['txt']
    lite: bool = False
    size_limit: Optional[int] = Field(
        default=51200,  # Default to 50 KB
        ge=1024,  # Minimum 1 KB
        le=104857600,  # Maximum 100 MB
        description="Maximum file size in bytes."
    )

class ScanResponse(BaseModel):
    scan_id: str
    repo_name: Optional[str] = None
    timestamp: Optional[str] = None
    summary: Dict
    directory_tree: str
    file_types: Dict[str, List[str]]
