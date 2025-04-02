import tempfile
import asyncio
import subprocess
import time
from pathlib import Path
from src.gittxt.core.scanner import Scanner
from src.gittxt.core.config import ConfigManager
from src.gittxt_api.models.scan import ScanRequest
from src.gittxt_api.utils.logger import get_logger
from src.gittxt_api.utils.task_registry import update_task, TaskStatus

logger = get_logger("scan_service")


async def scan_repo_logic(request: ScanRequest) -> dict:
    temp_dir = tempfile.mkdtemp()
    try:
        # Step 1: Clone repo into temp_dir
        logger.info(f"⏬ Cloning {request.repo_url} into {temp_dir}")
        subprocess.run(
            ["git", "clone", request.repo_url, temp_dir],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Step 2: Build scan path
        scan_path = Path(temp_dir)
        if request.subdir:
            scan_path = scan_path / request.subdir

        if not scan_path.exists():
            raise FileNotFoundError(f"Scan path does not exist: {scan_path}")

        # Step 3: Load and override config
        config = ConfigManager.load_config()
        logger.debug(f"🔧 Base config: {config}")

        scanner = Scanner(
            root_path=scan_path,
            exclude_dirs=config["filters"]["excluded_dirs"],
            size_limit=request.size_limit,
            include_patterns=request.include_patterns,
            exclude_patterns=request.exclude_patterns,
            verbose=(request.log_level == "debug"),
            use_ignore_file=True,
        )

        logger.info(f"🧪 Scanning path: {scan_path}")

        # Step 4: Run the scan (async safe)
        accepted_files, non_textual_files = await scanner.scan_directory()

        return {
            "message": "Scan completed successfully",
            "output_dir": str(temp_dir),
            "summary": {
                "accepted_count": len(accepted_files),
                "non_textual_count": len(non_textual_files),
                "scanned_path": str(scan_path),
            },
            "manifest": {
                "accepted_files": [str(p) for p in accepted_files],
                "non_textual_files": [str(p) for p in non_textual_files],
            },
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
