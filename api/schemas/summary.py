from pydantic import BaseModel
from typing import Dict, Optional

class SummaryResponse(BaseModel):
    scan_id: str
    repo_name: str
    branch: Optional[str]
    total_files: int
    total_size_bytes: int
    estimated_tokens: int
    file_type_breakdown: Dict[str, int]
    formatted: Dict[str, str]
