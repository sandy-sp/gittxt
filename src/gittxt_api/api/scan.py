from fastapi import APIRouter, HTTPException, BackgroundTasks
from gittxt_api.models.scan import ScanRequest, ScanResponse
from gittxt_api.services.scan_service import perform_scan, scan_repo_logic_async
from gittxt_api.utils.task_registry import (
    create_task,
    get_task,
    TaskStatus,
    task_registry,
)
from gittxt_api.utils.logger import get_logger

router = APIRouter()
logger = get_logger("scan_api")


@router.post("/", response_model=ScanResponse)
async def scan_repo(request: ScanRequest):
    try:
        return await perform_scan(request)
    except Exception as e:
        logger.exception(f"Scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/async")
async def scan_repo_background(request: ScanRequest, background_tasks: BackgroundTasks):
    # Validate first before registering task
    try:
        request = ScanRequest(**request.dict())  # trigger validation
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid scan request: {e}")

    task_id = create_task()
    background_tasks.add_task(scan_repo_logic_async, request, task_id)
    return {"task_id": task_id, "status": TaskStatus.PENDING}


@router.get("/status/{task_id}")
async def scan_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task ID not found")
    return {"status": task["status"], "error": task.get("error")}


@router.get("/result/{task_id}", response_model=ScanResponse)
async def scan_result(task_id: str):
    task = get_task(task_id)
    if not task or task["status"] != TaskStatus.COMPLETED:
        raise HTTPException(status_code=404, detail="Result not available yet.")
    return ScanResponse(**task["result"])


@router.get("/list")
async def list_tasks():
    return [
        {"task_id": task_id, "status": data["status"]}
        for task_id, data in task_registry.items()
    ]
