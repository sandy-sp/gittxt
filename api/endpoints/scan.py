from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.gittxt_runner import run_gittxt_scan

router = APIRouter()

class ScanRequest(BaseModel):
    repo_url: str
    options: dict = {}

@router.post("/")
async def scan_repo(req: ScanRequest):
    try:
        result = run_gittxt_scan(req.repo_url, req.options)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
