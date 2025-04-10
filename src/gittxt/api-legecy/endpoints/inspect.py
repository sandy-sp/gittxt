from fastapi import APIRouter, HTTPException, Query
import shutil
from uuid import uuid4
from pathlib import Path

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

@router.post("/inspect", tags=["Inspect"])
async def inspect_repo(
    repo_path: str,
    branch: str = None,
    exclude_dirs: list[str] = Query(default=[]),
    include_patterns: list[str] = Query(default=[]),
    exclude_patterns: list[str] = Query(default=[]),
):
    """
    Minimal 'inspect' endpoint. 
    We'll do a normal scan, but we only generate a .json in "rich" mode, 
    then read that .json and return it inline. 
    Then we cleanup the directory after returning the data
    (since you said you want just a ephemeral check).
    """
    try:
        scan_id = str(uuid4())
        scan_output_dir = OUTPUT_DIR / scan_id
        scan_output_dir.mkdir(parents=True, exist_ok=True)

        # 1) clone or local
        handler = RepositoryHandler(source=repo_path, branch=branch)
        await handler.resolve()
        local_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()

        # 2) merges
        merged_exclude_dirs = set(EXCLUDED_DIRS_DEFAULT) | set(exclude_dirs)
        # Optionally load .gittxtignore
        dynamic_ignores = load_gittxtignore(Path(local_path))
        merged_exclude_dirs |= set(dynamic_ignores)

        # 3) scanner
        target_root = Path(local_path) / subdir if subdir else Path(local_path)
        scanner = Scanner(
            root_path=target_root,
            exclude_dirs=list(merged_exclude_dirs),
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )
        textual_files, non_textual_files = await scanner.scan_directory()

        # 4) builder, but only want .json, "rich" mode
        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=scan_output_dir,
            output_format="json",
            repo_url=repo_path if is_remote else None,
            branch=used_branch,
            subdir=subdir,
            mode="rich",  # you said you want "rich" mode
        )
        await builder.generate_output(
            textual_files, non_textual_files, repo_path=target_root, 
            create_zip=False
        )

        # If remote, remove the clone
        if is_remote:
            cleanup_temp_folder(Path(local_path))

        # 5) read the generated .json
        json_dir = scan_output_dir / "json"
        # Usually there's exactly 1 .json. Let's pick the first
        files = list(json_dir.glob("*.json"))
        if not files:
            raise HTTPException(status_code=404, detail="No JSON artifact found")
        artifact = files[0]

        # parse content
        import json
        data = json.loads(artifact.read_text(encoding="utf-8"))

        # ephemeral => cleanup after we read the content
        shutil.rmtree(scan_output_dir, ignore_errors=True)

        # Return the JSON content inline
        return data

    except Exception as e:
        logger.error(f"[INSPECT] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
