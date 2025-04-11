from pydantic import BaseModel

class UploadResponse(BaseModel):
    scan_id: str
    repo_name: str
    num_textual_files: int
    num_non_textual_files: int
    message: str
