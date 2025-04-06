from pydantic import BaseModel
from typing import List, Dict, Optional, Union

class InspectRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None
    subdir: Optional[str] = None

class PreviewSnippet(BaseModel):
    path: str
    preview: str

class InspectResponse(BaseModel):
    repo_name: str
    branch: Optional[str]
    tree: Union[Dict, List]  # List fallback in case of JSON-converted tree
    textual_files: List[str]
    non_textual_files: List[str]
    summary: Dict[str, Union[int, str, Dict[str, int]]]
    preview_snippets: List[PreviewSnippet]
