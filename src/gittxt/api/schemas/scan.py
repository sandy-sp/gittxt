from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ScanRequest(BaseModel):
    """Request model for repository scanning"""
    repo_url: str = Field(..., description="URL of the GitHub repository to scan")
    output_formats: List[str] = Field(default=["txt"], description="Output formats to generate")
    lite: bool = Field(default=False, description="Whether to use lite mode")
    include_patterns: Optional[List[str]] = Field(None, description="Glob patterns to include")
    exclude_patterns: Optional[List[str]] = Field(None, description="Glob patterns to exclude")
    exclude_dirs: Optional[List[str]] = Field(None, description="Directories to exclude")
    branch: Optional[str] = Field(None, description="Git branch for remote repos")
    callback_host: Optional[str] = Field(None, description="Host URL for download links")

class DownloadURLs(BaseModel):
    """URLs for downloading scan outputs"""
    txt_url: Optional[str] = Field(None, description="URL to download TXT output")
    json_url: Optional[str] = Field(None, description="URL to download JSON output")
    md_url: Optional[str] = Field(None, description="URL to download Markdown output")
    zip_url: Optional[str] = Field(None, description="URL to download ZIP archive")

class ScanResponse(BaseModel):
    """Response model for repository scanning"""
    scan_id: str
    repo_name: str
    file_count: int
    download_urls: Dict[str, Optional[str]]
    status: str = "completed"
