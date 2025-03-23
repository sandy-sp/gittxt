import asyncio
from pathlib import Path
from typing import List, Optional
from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.logger import Logger

SCANS = {}
MAX_CONCURRENT_SCANS = 1
SEM = asyncio.Semaphore(MAX_CONCURRENT_SCANS)

logger = Logger.get_logger(__name__)

async def run_scan_task(
    scan_id: str,
    repo_url: str,
    file_types: List[str],
    output_format: str,
    progress_callback,
    include_patterns: List[str],
    exclude_patterns: List[str],
    size_limit: Optional[int],
    branch: Optional[str],
    tree_depth: Optional[int],
    create_zip: Optional[bool]
):
    async with SEM:
        SCANS[scan_id]["status"] = "running"
        try:
            repo_handler = RepositoryHandler(source=repo_url, branch=branch)
            repo_path, subdir, is_remote, repo_name = repo_handler.get_local_path()
            if not repo_path:
                raise ValueError("Invalid repo or local path")

            scan_root = Path(repo_path)
            if subdir:
                scan_root = scan_root / subdir

            # New CLI-aligned scanner logic
            scanner = Scanner(
                root_path=scan_root,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                size_limit=size_limit,
                file_types=file_types,
                progress=False
            )

            all_files, _ = scanner.scan_directory()
            total_count = len(all_files)

            # Progress callback
            for idx, path in enumerate(all_files):
                _emit(scan_id, idx, total_count, f"Accepted {path.name}", progress_callback)
                await asyncio.sleep(0)

            if not all_files:
                SCANS[scan_id].update({
                    "status": "done",
                    "file_count": 0,
                    "message": "No valid files found."
                })
                return

            output_dir = Path.cwd() / f"scan_{scan_id}_outputs"
            builder = OutputBuilder(
                repo_name=repo_name,
                output_dir=output_dir,
                output_format=output_format,
                repo_url=repo_url if is_remote else None
            )

            _emit(scan_id, total_count, total_count, "Generating outputs...", progress_callback)

            # Call new generate_output with unified file list
            await builder.generate_output(all_files, repo_path, create_zip=create_zip, tree_depth=tree_depth)

            SCANS[scan_id].update({
                "status": "done",
                "message": "Scan complete",
                "file_count": len(all_files),
                "output_dir": str(output_dir),
                "repo_name": repo_name
            })
            logger.info(f"Scan {scan_id} completed -> {output_dir}")

        except Exception as e:
            SCANS[scan_id]["status"] = "error"
            SCANS[scan_id]["error"] = str(e)
            logger.error(f"Scan {scan_id} failed: {e}")

        finally:
            if is_remote:
                cleanup_temp_folder(Path(repo_path))

def _emit(scan_id, current, total, msg, cb):
    if scan_id in SCANS:
        progress = round((current / total) * 100, 2) if total else 0
        SCANS[scan_id]["progress"] = progress
        SCANS[scan_id]["current_file"] = msg
        cb(scan_id, current, total, msg)

def update_scan_progress(scan_id: str, current: int, total: int, msg: str):
    logger.debug(f"[{scan_id}] Progress: {msg} ({current}/{total})")
