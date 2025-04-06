from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from uuid import UUID

class OutputFormat(str, Enum):
    txt = "txt"
    md = "md"
    json = "json"
    zip = "zip"

class ScanRequest(BaseModel):
    """Request model for repository scanning"""
    repo_path: str = Field(..., description="Path to the repository to scan")
    output_formats: List[str] = Field(["txt"], description="Output formats to generate")
    lite: bool = Field(False, description="Whether to use lite mode")
    include_patterns: Optional[List[str]] = Field(None, description="Glob patterns to include")
    exclude_patterns: Optional[List[str]] = Field(None, description="Glob patterns to exclude")
    exclude_dirs: Optional[List[str]] = Field(None, description="Directories to exclude")
    branch: Optional[str] = Field(None, description="Git branch for remote repos")

class DownloadURLs(BaseModel):
    """Download URLs for scan outputs"""
    txt: Optional[str] = Field(None, description="URL to download TXT output")
    json: Optional[str] = Field(None, description="URL to download JSON output")
    md: Optional[str] = Field(None, description="URL to download Markdown output")
    zip: Optional[str] = Field(None, description="URL to download ZIP archive")

class ScanResponse(BaseModel):
    """Response model for repository scanning"""
    scan_id: str = Field(..., description="Unique ID for this scan")
    repo_name: str = Field(..., description="Name of the repository")
    file_count: int = Field(..., description="Number of textual files")
    download_urls: DownloadURLs = Field(..., description="URLs to download outputs")
    status: str = Field("completed", description="Status of the scan")
