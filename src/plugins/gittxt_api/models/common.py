from pydantic import BaseModel

class RepoBase(BaseModel):
    repo_path: str
    branch: str | None = None
