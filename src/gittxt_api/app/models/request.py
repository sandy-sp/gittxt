from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class ScanRequest(BaseModel):
    repo_url: HttpUrl = Field(..., description="GitHub repository HTTPS URL")
    branch: Optional[str] = Field(None, description="Git branch (optional)")
    subdir: Optional[str] = Field(None, description="Subdirectory inside repo")

    exclude_dirs: Optional[List[str]] = Field(default_factory=list, description="Directories to exclude")
    exclude_patterns: Optional[List[str]] = Field(default_factory=list, description="File patterns to exclude (e.g. '*.md')")
    include_patterns: Optional[List[str]] = Field(default_factory=list, description="File patterns to include (e.g. '*.py')")

    size_limit_kb: Optional[int] = Field(0, description="Max file size in KB (0 means no limit)")
    tree_depth: Optional[int] = Field(3, description="Depth of directory tree to return")
    output_formats: Optional[List[str]] = Field(default_factory=lambda: ["json"], description="List of output formats (txt, json, md)")

    lite: Optional[bool] = Field(False, description="Enable lite mode (minimal output)")
    zip: Optional[bool] = Field(False, description="Bundle output as ZIP")
    sync: Optional[bool] = Field(False, description="Enable .gittxtignore sync")
