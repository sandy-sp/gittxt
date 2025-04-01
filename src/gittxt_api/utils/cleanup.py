import asyncio
import shutil
import time
from gittxt_api.utils.task_registry import task_registry, TaskStatus

TTL_SECONDS = 600  # 10 minutes

async def cleanup_worker():
    while True:
        now = time.time()
        to_delete = []

        for task_id, task in task_registry.items():
            result = task.get("result", {})
            path = result.get("__cleanup_path__")

            if task["status"] == TaskStatus.COMPLETED and path:
                created_at = result.get("__timestamp__", now)
                if now - created_at > TTL_SECONDS:
                    to_delete.append((task_id, path))

        for task_id, path in to_delete:
            try:
                shutil.rmtree(path, ignore_errors=True)
                task_registry[task_id]["result"]["__cleanup_path__"] = None
                print(f"[CLEANUP] Deleted: {path}")
            except Exception as e:
                print(f"[CLEANUP ERROR] Failed to delete {path}: {e}")

        await asyncio.sleep(60)  # Run cleanup every minute
