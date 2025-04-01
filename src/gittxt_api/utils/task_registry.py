import uuid
from enum import Enum
from typing import Dict

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Global in-memory task store
task_registry: Dict[str, Dict] = {}

def create_task() -> str:
    task_id = str(uuid.uuid4())
    task_registry[task_id] = {"status": TaskStatus.PENDING, "result": None, "error": None}
    return task_id

def update_task(task_id: str, status: TaskStatus, result=None, error=None):
    task_registry[task_id] = {
        "status": status,
        "result": result,
        "error": error
    }

def get_task(task_id: str):
    return task_registry.get(task_id, None)
