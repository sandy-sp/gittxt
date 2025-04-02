import asyncio
import os
from gittxt_api.utils.logger import get_logger

logger = get_logger("cleanup")

# Background cleanup loop
async def cleanup_worker():
    from gittxt_api.utils.task_registry import task_registry
    while True:
        await asyncio.sleep(600)  # every 10 minutes
        for task_id, task in list(task_registry.items()):
            result = task.get("result")
            if not isinstance(result, dict):
                continue
            path = result.get("__cleanup_path")
            if path and os.path.exists(path):
                try:
                    os.system(f"rm -rf '{path}'")
                    logger.info(f"Cleaned up temp dir for task {task_id}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup for {task_id}: {e}")
