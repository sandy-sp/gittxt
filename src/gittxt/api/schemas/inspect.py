from pydantic import BaseModel
from typing import Dict

class InspectRequest(BaseModel):
    repo_path: str  # Path to the repository to inspect

class PreviewSnippet(BaseModel):
    path: str
    preview: str

class InspectResponse(BaseModel):
    repo_name: str
    tree: Dict  # Simplified to Dict
    file_count: int
    folder_count: int
