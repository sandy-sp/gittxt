from fastapi import APIRouter, HTTPException
from gittxt_api.models.scan import ScanRequest, ScanResponse
from gittxt_api.services.scan_service import scan_repo_logic
from fastapi import BackgroundTasks
from gittxt_api.utils.task_registry import create_task, update_task, get_task, TaskStatus
from gittxt_api.services.scan_service import scan_repo_logic_async

router = APIRouter()

@router.post("/", response_model=ScanResponse)
async def scan_repo(request: ScanRequest):
    try:
        result = await scan_repo_logic(request)
        return ScanResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/async")
async def scan_repo_background(request: ScanRequest, background_tasks: BackgroundTasks):
    task_id = create_task()

    # Run scanner logic in the background
    background_tasks.add_task(scan_repo_logic_async, request, task_id)

    return {"task_id": task_id, "status": TaskStatus.PENDING}


@router.get("/status/{task_id}")
async def scan_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task ID not found")
    return task
