from pydantic import BaseModel, Field
from typing import Dict, Optional, List

class FileBreakdown(BaseModel):
    file_type: str = Field(..., description="Category or type of file (e.g., Python, Markdown)")
    count: int = Field(..., description="Number of files of this type")
    estimated_tokens_formatted: str = Field(..., description="Estimated token count for this type (formatted string)")

class SummaryResponse(BaseModel):
    scan_id: str
    repo_name: str
    branch: Optional[str]
    total_files: int
    total_size_bytes: int
    estimated_tokens: int
    file_type_breakdown: List[FileBreakdown]  # Updated to use FileBreakdown model
    formatted: Dict[str, str]
    summary: dict  # Detailed summary data
    artifacts: Dict[str, Optional[str]]  # Paths to generated artifacts (e.g., JSON, TXT, MD)
