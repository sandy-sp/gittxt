import tempfile
import asyncio
import time
from src.gittxt.core.scanner import Scanner
from src.gittxt.core.config import ConfigManager
from src.gittxt_api.models.scan import ScanRequest
from src.gittxt_api.utils.logger import get_logger
from src.gittxt_api.utils.task_registry import update_task, TaskStatus

logger = get_logger("scan_service")

async def scan_repo_logic(request: ScanRequest) -> dict:
    temp_dir = tempfile.mkdtemp()
    try:
        # Create config for Gittxt Scanner
        config = ConfigManager.load_config()

        # Override dynamic runtime config
        config["output_dir"] = temp_dir
        config["output_format"] = request.output_format
        config["auto_zip"] = request.zip
        config["lite"] = request.lite
        config["branch"] = request.branch
        config["subdir"] = request.subdir
        config["include_patterns"] = request.include_patterns
        config["exclude_patterns"] = request.exclude_patterns
        config["size_limit"] = request.size_limit
        config["tree_depth"] = request.tree_depth
        config["logging_level"] = request.log_level or config.get("logging_level", "info")
        config["sync"] = request.sync

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
        logger.error(f"Scan failed: {e}", exc_info=True)
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
