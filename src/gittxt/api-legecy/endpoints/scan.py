from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from uuid import uuid4

from gittxt.core.logger import Logger
from gittxt.core.config import ConfigManager
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT
from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.utils.file_utils import load_gittxtignore

router = APIRouter()
logger = Logger.get_logger(__name__)
config = ConfigManager.load_config()

OUTPUT_DIR = Path(config.get("output_dir", "./gittxt_output")).resolve()

@router.post("/scan", tags=["Scan"])
async def scan_repository(
    repo_path: str,
    branch: str = None,
    exclude_dirs: list[str] = Query(default=[]),
    include_patterns: list[str] = Query(default=[]),
    exclude_patterns: list[str] = Query(default=[]),
    lite: bool = False,
):
    """
    Standard full-mode scan. Writes .txt, .json, .md subfolders, 
    optionally produce a .zip if you want it.
    """
    try:
        scan_id = str(uuid4())
        scan_output_dir = OUTPUT_DIR / scan_id
        scan_output_dir.mkdir(parents=True, exist_ok=True)

        # clone or local
        handler = RepositoryHandler(source=repo_path, branch=branch)
        await handler.resolve()
        local_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()

        # merges
        merged_exclude_dirs = set(EXCLUDED_DIRS_DEFAULT) | set(exclude_dirs)
        if lite:
            dynamic_ignores = load_gittxtignore(Path(local_path))
            merged_exclude_dirs |= set(dynamic_ignores)

        target_root = Path(local_path) / subdir if subdir else Path(local_path)
        scanner = Scanner(
            root_path=target_root,
            exclude_dirs=list(merged_exclude_dirs),
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
        textual_files, non_textual_files = await scanner.scan_directory()

        # outputs
        mode = "lite" if lite else "rich"
        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=scan_output_dir,
            output_format="txt,json,md",
            repo_url=repo_path if is_remote else None,
            branch=used_branch,
            subdir=subdir,
            mode=mode,
        )
        await builder.generate_output(
            textual_files, non_textual_files, repo_path=target_root,
            create_zip=False  # or True if you want a .zip
        )

        if is_remote:
            cleanup_temp_folder(Path(local_path))

        return {
            "scan_id": scan_id,
            "repo_name": repo_name,
            "num_textual_files": len(textual_files),
            "num_non_textual_files": len(non_textual_files),
            "artifact_dir": str(scan_output_dir),
            "message": "Scan completed"
        }

    except Exception as e:
        logger.error(f"[SCAN] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
