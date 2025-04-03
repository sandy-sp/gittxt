import uuid
import time
from enum import Enum
from typing import Dict, Optional

TASK_TTL_SECONDS = 600  # 10 minutes default

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Global in-memory task store
task_registry: Dict[str, Dict] = {}

def create_task() -> str:
    task_id = str(uuid.uuid4())
    task_registry[task_id] = {
        "status": TaskStatus.PENDING,
        "result": None,
        "error": None,
        "__timestamp": time.time()
    }
    return task_id

def update_task(task_id: str, status: TaskStatus, result=None, error=None):
    task = task_registry.get(task_id)
    if not task:
        return
    task.update({
        "status": status,
        "result": result,
        "error": error,
        "__timestamp": time.time()
    })

def get_task(task_id: str) -> Optional[Dict]:
    cleanup_expired_tasks()
    return task_registry.get(task_id)

def get_all_tasks() -> Dict[str, Dict]:
    cleanup_expired_tasks()
    return task_registry

def cleanup_expired_tasks():
    now = time.time()
    expired = [
        task_id for task_id, data in task_registry.items()
        if data["status"] in {TaskStatus.COMPLETED, TaskStatus.FAILED}
        and (now - data.get("__timestamp", 0)) > TASK_TTL_SECONDS
    ]
    for task_id in expired:
        del task_registry[task_id]
