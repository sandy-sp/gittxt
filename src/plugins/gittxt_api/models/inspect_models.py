from pydantic import BaseModel
from typing import Optional, List

class InspectRequest(BaseModel):
    repo_path: str
    branch: Optional[str] = None
    exclude_dirs: Optional[List[str]] = []
    include_patterns: Optional[List[str]] = []
    exclude_patterns: Optional[List[str]] = []
