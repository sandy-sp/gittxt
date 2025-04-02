import tempfile
import asyncio
import time
from gittxt.core.scanner import Scanner
from gittxt.core.config import GittxtConfig
from gittxt_api.models.scan import ScanRequest
from gittxt_api.utils.logger import get_logger
from gittxt_api.utils.task_registry import update_task, TaskStatus

logger = get_logger("scan_service")

async def scan_repo_logic(request: ScanRequest) -> dict:
    temp_dir = tempfile.mkdtemp()
    try:
        # Create config for Gittxt Scanner
        config = GittxtConfig(
            output_dir=temp_dir,
            output_format=request.output_format,
            zip=request.zip,
            lite=request.lite,
            branch=request.branch,
            subdir=request.subdir,
            include_patterns=request.include_patterns,
            exclude_patterns=request.exclude_patterns,
            size_limit=request.size_limit,
            tree_depth=request.tree_depth,
            log_level=request.log_level or "info",
            sync=request.sync,
        )

        scanner = Scanner(config=config)

        # Run scan in a thread-safe async way
        result = await asyncio.to_thread(scanner.scan, request.repo_url)

        return {
            "message": "Scan completed successfully",
            "output_dir": temp_dir,
            "summary": result.summary,
            "manifest": result.manifest,
        }

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise

async def scan_repo_logic_async(request: ScanRequest, task_id: str):
    try:
        update_task(task_id, TaskStatus.RUNNING)

        result = await scan_repo_logic(request)

        result["__cleanup_path__"] = result["output_dir"]
        result["__timestamp__"] = time.time()
        update_task(task_id, TaskStatus.COMPLETED, result=result)
    except Exception as e:
        update_task(task_id, TaskStatus.FAILED, error=str(e))
