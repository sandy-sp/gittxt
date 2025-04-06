from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any

class FileBreakdown(BaseModel):
    file_type: str = Field(..., description="Category or type of file (e.g., Python, Markdown)")
    count: int = Field(..., description="Number of files of this type")
    estimated_tokens_formatted: str = Field(..., description="Estimated token count for this type (formatted string)")

class FileSummary(BaseModel):
    """Summary information for a file"""
    path: str = Field(..., description="Path to the file")
    size: int = Field(..., description="Size of the file in bytes")
    line_count: int = Field(..., description="Number of lines in the file")
    extension: str = Field(..., description="File extension")

class LanguageSummary(BaseModel):
    """Summary information for a programming language"""
    name: str = Field(..., description="Language name")
    file_count: int = Field(..., description="Number of files")
    line_count: int = Field(..., description="Total number of lines")
    percentage: float = Field(..., description="Percentage of the repository")

class SummaryResponse(BaseModel):
    """Response model for scan summary"""
    scan_id: str = Field(..., description="Unique ID for this scan")
    repo_name: str = Field(..., description="Name of the repository")
    total_files: int = Field(..., description="Total number of files")
    total_lines: int = Field(..., description="Total number of lines")
    languages: List[LanguageSummary] = Field(default_factory=list, description="Language statistics")
    largest_files: List[FileSummary] = Field(default_factory=list, description="Largest files in the repository")
    oldest_files: Optional[List[FileSummary]] = Field(None, description="Oldest files in the repository")
    most_recently_modified: Optional[List[FileSummary]] = Field(None, description="Most recently modified files")
