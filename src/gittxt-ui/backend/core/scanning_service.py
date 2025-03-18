# src/gittxt-ui/backend/core/scanning_service.py

import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import uuid

from gittxt.repository import RepositoryHandler
from gittxt.scanner import Scanner
from gittxt.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.logger import Logger

logger = Logger.get_logger(__name__)

# Keep track of each scan's status in memory
SCANS: Dict[str, dict] = {}

# Concurrency limit: only one scan at a time
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
):
    """
    The main background task for scanning. 
    1) Acquire a concurrency semaphore (so only 1 concurrent scan).
    2) Clone or validate local repo.
    3) Perform a custom scanning loop with partial progress updates.
    4) If valid files found, generate Gittxt artifacts with the real repo/folder name.
    5) Store ephemeral outputs in a folder named after both the repo/folder name and the scan_id.
    6) If remote, remove the cloned repo afterwards, but keep ephemeral outputs for user to download.
    """
    async with SEM:
        SCANS[scan_id]["status"] = "running"
        try:
            # 1) Prepare the repository (clone or check local).
            repo_handler = RepositoryHandler(source=repo_url, branch=branch)
            repo_path, subdir, is_remote = repo_handler.get_local_path()
            if not repo_path:
                raise ValueError("Repository path is invalid or does not exist.")

            # If user specified a subdirectory
            scan_root = Path(repo_path)
            if subdir:
                scan_root = scan_root / subdir

            # Derive the real folder name from the local path or remote clone
            repo_dir_name = Path(repo_path).name  # e.g. "gittxt" or "MyRepo"

            # 2) Perform scanning with partial progress updates
            valid_files, tree_summary = await _scan_with_custom_progress(
                scan_id,
                scan_root,
                file_types,
                progress_callback,
                include_patterns,
                exclude_patterns,
                size_limit
            )

            # 3) If no valid files, wrap up early
            if not valid_files:
                SCANS[scan_id].update({
                    "status": "done",
                    "file_count": 0,
                    "message": "No valid files found."
                })
                return

            # 4) Build ephemeral output dir
            #    If you want to keep the random ID for uniqueness, 
            #    but still see the real repo name, you can do:
            output_dir = Path.cwd() / f"{repo_dir_name}_scan_{scan_id}_outputs"

            # 5) Create Gittxt artifacts using the real folder name
            builder = OutputBuilder(
                repo_name=repo_dir_name,  # This ensures .txt, .md, .json, etc. have the real name
                output_dir=output_dir,
                output_format=output_format
            )
            builder.generate_output(valid_files, scan_root)

            # 6) Update SCANS dict
            SCANS[scan_id].update({
                "status": "done",
                "message": "Scan complete",
                "file_count": len(valid_files),
                "tree_summary": tree_summary,
                "output_dir": str(output_dir)
            })
            logger.info(
                f"Scan {scan_id} completed successfully. "
                f"Artifacts in: {output_dir}"
            )

        except Exception as e:
            # If an exception occurs, mark the scan as error
            SCANS[scan_id]["status"] = "error"
            SCANS[scan_id]["error"] = str(e)
            logger.error(f"Scan {scan_id} failed with error: {e}")

        finally:
            # 7) If remote, remove the cloned repo so we don't keep big ephemeral clones.
            #    We do NOT remove the ephemeral output_dir here, 
            #    so the user can still download artifacts.
            if is_remote:
                cleanup_temp_folder(Path(repo_path))


async def _scan_with_custom_progress(
    scan_id: str,
    scan_root: Path,
    file_types: List[str],
    progress_callback,
    include_patterns: List[str],
    exclude_patterns: List[str],
    size_limit: Optional[int],
):
    """
    A custom scanning approach that calls progress_callback after each file is visited.
    The default Gittxt logic is used (via scanner._passes_* methods), 
    but we handle the iteration manually for real-time progress updates.
    """
    scanner = Scanner(
        root_path=scan_root,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        size_limit=size_limit,
        file_types=file_types,
        progress=False  # We'll do our own manual progress
    )

    all_paths = list(scan_root.rglob("*"))
    total_count = len(all_paths)
    current_count = 0

    valid_files = []

    for path in all_paths:
        current_count += 1
        # If not a file (e.g. directory, symlink, etc.)
        if not path.is_file():
            progress_callback(scan_id, current_count, total_count,
                              f"Skipping dir {path.name}")
            continue

        # If it doesn't pass Gittxt filters
        if not scanner._passes_filters(path):
            progress_callback(scan_id, current_count, total_count,
                              f"Excluded {path.name}")
            continue
        if not scanner._passes_filetype_filter(path):
            progress_callback(scan_id, current_count, total_count,
                              f"Skipping type {path.name}")
            continue

        valid_files.append(path.resolve())
        progress_callback(scan_id, current_count, total_count, 
                          f"Scanned {path.name}")

        # Small async sleep so event loop can handle other tasks
        await asyncio.sleep(0)

    # After scanning, we can still use the Gittxt approach to build a final tree
    # or just pass along our own results. Here we call the "sync" method:
    tree_summary = scanner._scan_directory_sync()[1]
    return valid_files, tree_summary


def update_scan_progress(scan_id: str, current: int, total: int, msg: str):
    """
    A callback function that updates SCANS dict to reflect ongoing progress.
    Typically called after each file is processed in _scan_with_custom_progress.
    """
    if scan_id in SCANS:
        progress = round((current / total) * 100, 2)
        SCANS[scan_id]["progress"] = progress
        SCANS[scan_id]["current_file"] = msg


def build_directory_tree(base_path: Path) -> dict:
    """
    Recursively build a nested dict describing folders/files for a 'tree' endpoint.
    """
    if not base_path.is_dir():
        return {"name": base_path.name, "type": "file"}

    node = {"name": base_path.name, "type": "directory", "children": []}
    for child in sorted(base_path.iterdir(), key=lambda c: c.name.lower()):
        if child.is_dir():
            node["children"].append(build_directory_tree(child))
        else:
            node["children"].append({"name": child.name, "type": "file"})
    return node


def gather_file_extensions(root: Path) -> dict:
    """
    Collects file extensions (suffixes) from all files under 'root'.
    Returns a dict like:
      {
        ".py": 14,
        ".md": 6,
        ".json": 2,
        ...
      }
    representing how many times each extension appears.
    """
    ext_map = {}
    for f in root.rglob("*"):
        if f.is_file():
            suffix = f.suffix.lower()
            ext_map[suffix] = ext_map.get(suffix, 0) + 1
    return ext_map


def remove_ephemeral_outputs(path_obj: Path):
    """
    Removes ephemeral artifacts from 'path_obj' using the existing 
    cleanup_temp_folder() from gittxt.utils.cleanup_utils.
    Typically called by /scans/{scan_id}/close to free up disk space 
    after user finishes with the artifacts.
    """
    if path_obj.exists():
        cleanup_temp_folder(path_obj)
