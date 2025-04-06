from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class OutputFormat(str, Enum):
    txt = "txt"
    md = "md"
    json = "json"
    zip = "zip"

class ScanRequest(BaseModel):
    repo_url: str = Field(..., description="URL of the Git repository (e.g., GitHub, GitLab)")
    branch: Optional[str] = Field(None, description="Specific branch to scan (default: repo's default)")
    subdir: Optional[str] = Field(None, description="Specific subdirectory within the repo to scan")
    output_formats: List[OutputFormat] = Field(default=[OutputFormat.txt, OutputFormat.zip], description="List of desired output formats")
    exclude_dirs: Optional[List[str]] = Field(default=None, description="List of directory names or paths relative to repo root to exclude")
    exclude_patterns: Optional[List[str]] = Field(default=None, description="List of glob patterns to exclude files/folders")
    include_patterns: Optional[List[str]] = Field(default=None, description="List of glob patterns to include specific textual files (overrides default textual identification)")
    size_limit: Optional[int] = Field(default=None, description="Maximum individual file size in bytes to process")
    sync: bool = Field(default=False, description="Enable synchronization with .gitignore/.gittxtignore files found in the repo")
    lite: bool = Field(default=False, description="Generate minimal output (file list, tree, summary) instead of full content")
    tree_depth: Optional[int] = Field(default=None, description="Maximum depth for the directory tree output")

class DownloadURLs(BaseModel):
    txt: Optional[str] = None
    md: Optional[str] = None
    json_url: Optional[str] = None  # Renamed from 'json'
    zip: Optional[str] = None

class ScanResponse(BaseModel):
    scan_id: str = Field(..., description="Unique identifier for this scan session")
    repo_name: str = Field(..., description="Name of the repository being scanned")
    status: str = Field(default="initiated", description="Current status of the scan (e.g., initiated, running, completed, failed)")
    message: Optional[str] = Field(None, description="Additional information about the scan status")
    download_base_url: Optional[str] = Field(None, description="Base URL pattern for downloading results (append /{repo_name}/{format})")
    cleanup_url: Optional[str] = Field(None, description="URL for cleaning up scan artifacts")
    summary_url: Optional[str] = Field(None, description="URL for retrieving the scan summary")
    summary: Dict
    download_urls: DownloadURLs
