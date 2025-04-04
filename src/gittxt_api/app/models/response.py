from typing import Dict, List, Optional, Union
from pydantic import BaseModel


class FileMetadata(BaseModel):
    path: str
    type: str
    size_kb: float
    token_count: int


class TreeNode(BaseModel):
    name: str
    children: Optional[List['TreeNode']] = None


TreeNode.update_forward_refs()


class ScanSummary(BaseModel):
    file_count: int
    token_count: int
    language_breakdown: Dict[str, int]


class ScanResponse(BaseModel):
    status: str = "success"
    scan_id: str
    summary: ScanSummary
    tree: TreeNode
    file_metadata: List[FileMetadata]
    subcategory_breakdown: Dict[str, List[str]]
    download_links: Dict[str, str]


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
