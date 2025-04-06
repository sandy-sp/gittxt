from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/{scan_id}")
async def download_output(scan_id: str):
    # TODO: Serve ZIP or generated output file by ID
    raise HTTPException(status_code=501, detail="Download not implemented")
