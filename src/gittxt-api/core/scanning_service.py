import asyncio
from pathlib import Path
from typing import List, Optional
from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.logger import Logger
from services.tree_service import build_directory_tree, gather_file_extensions

logger = Logger.get_logger(__name__)

SCANS = {}
MAX_CONCURRENT_SCANS = 1
SEM = asyncio.Semaphore(MAX_CONCURRENT_SCANS)

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
            repo_path, subdir, is_remote = repo_handler.get_local_path()
            if not repo_path:
                raise ValueError("Invalid repo or local path")

            scan_root = Path(repo_path)
            if subdir:
                scan_root = scan_root / subdir

            repo_dir_name = Path(repo_path).name

            scanner = Scanner(
                root_path=scan_root,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                size_limit=size_limit,
                file_types=file_types,
                progress=False,
                tree_depth=tree_depth
            )

            # ✅ Use scanner API directly (avoid redundant filtering)
            valid_files, _ = scanner.scan_directory()
            total_count = len(valid_files)

            for idx, path in enumerate(valid_files):
                _emit(scan_id, idx, total_count, f"Accepted {path.name}", progress_callback)
                await asyncio.sleep(0)

            if not valid_files:
                SCANS[scan_id].update({
                    "status": "done",
                    "file_count": 0,
                    "message": "No valid files found."
                })
                return

            output_dir = Path.cwd() / f"{repo_dir_name}_scan_{scan_id}_outputs"
            builder = OutputBuilder(
                repo_name=repo_dir_name,
                output_dir=output_dir,
                output_format=output_format
            )

            _emit(scan_id, total_count, total_count, "Generating outputs...", progress_callback)
            await builder.generate_output(valid_files, scan_root, create_zip=create_zip, tree_depth=tree_depth)

            SCANS[scan_id].update({
                "status": "done",
                "message": "Scan complete",
                "file_count": len(valid_files),
                "output_dir": str(output_dir),
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

# Utility re-exports
from services.tree_service import build_directory_tree, gather_file_extensions, remove_ephemeral_outputs

def update_scan_progress(scan_id: str, current: int, total: int, msg: str):
    logger.debug(f"[{scan_id}] Progress: {msg} ({current}/{total})")
