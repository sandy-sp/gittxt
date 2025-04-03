import asyncio
import os
import shutil
from gittxt_api.utils.logger import get_logger
from gittxt_api.utils.task_registry import task_registry

logger = get_logger("cleanup")


# Background cleanup loop
async def cleanup_worker():
    while True:
        await asyncio.sleep(600)  # every 10 minutes

        for task_id, task in list(task_registry.items()):
            result = task.get("result")
            if not isinstance(result, dict):
                continue

            path = result.get("__cleanup_path")
            if path and os.path.exists(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                    logger.info(f"Cleaned up temp dir for task {task_id}")
                except Exception as e:
                    logger.warning(f"Failed to clean up dir for {task_id}: {e}")
