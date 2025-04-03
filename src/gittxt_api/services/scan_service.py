import time
from pathlib import Path
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.core.repository import RepositoryHandler
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.utils.file_utils import load_gittxtignore  # <-- centralized
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT
from gittxt.utils.filetype_utils import FiletypeConfigManager

from gittxt_api.models.scan import ScanRequest, ScanResponse
from gittxt_api.utils.logger import get_logger
from gittxt_api.utils.task_registry import update_task, TaskStatus

logger = get_logger("scan_service")


async def perform_scan(request: ScanRequest) -> ScanResponse:
    try:
        # Step 1: Clone/resolve repository
        handler = RepositoryHandler(source=request.repo_url, branch=request.branch)
        await handler.resolve()
        repo_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()

        scan_root = Path(repo_path)
        if request.subdir:
            scan_root = scan_root / request.subdir
            try:
                scan_root.resolve().relative_to(Path(repo_path).resolve())
            except ValueError:
                raise Exception(f"Invalid subdir: {request.subdir} is outside repo")

        if not scan_root.exists():
            raise FileNotFoundError(f"Scan path does not exist: {scan_root}")

        # Step 2: Filters & exclusions
        dynamic_ignores = load_gittxtignore(scan_root) if request.sync_ignore else []
        exclude_dirs = list(
            set(request.exclude_dirs or [])
            | set(dynamic_ignores)
            | set(EXCLUDED_DIRS_DEFAULT)
        )

        for pattern in request.include_patterns or []:
            ext = Path(pattern).suffix.lower()
            if ext and not FiletypeConfigManager.is_known_textual_ext(ext):
                logger.warning(f"Include pattern targets non-textual extension: {ext}")

        # Step 3: Scan
        scanner = Scanner(
            root_path=scan_root,
            exclude_dirs=exclude_dirs,
            size_limit=request.size_limit,
            include_patterns=request.include_patterns,
            exclude_patterns=request.exclude_patterns,
            progress=False,
            use_ignore_file=request.sync_ignore,
        )
        textual_files, non_textual_files = await scanner.scan_directory()
        skipped_files = scanner.skipped_files

        if not textual_files:
            raise Exception("No valid textual files found.")

        # Step 4: Summary BEFORE output
        summary = await generate_summary(textual_files + non_textual_files)

        # Step 5: Build output
        output_dir = Path(request.output_dir).resolve()
        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=output_dir,
            output_format=request.output_format,
            repo_url=request.repo_url if is_remote else None,
            branch=used_branch,
            subdir=subdir,
            mode="lite" if request.lite_mode else "rich",
        )
        output_files = await builder.generate_output(
            textual_files,
            non_textual_files,
            repo_path,
            create_zip=request.create_zip,
            tree_depth=request.tree_depth,
        )

        return ScanResponse(
            repo_name=repo_name,
            output_dir=str(output_dir),
            output_files=[str(p) for p in output_files],
            total_files=summary.get("total_files", 0),
            total_size_bytes=summary.get("total_size", 0),
            estimated_tokens=summary.get("estimated_tokens", 0),
            file_type_breakdown=summary.get("file_type_breakdown", {}),
            tokens_by_type=summary.get("tokens_by_type", {}),
            skipped_files=[(str(p), reason) for p, reason in skipped_files],
        )

    finally:
        if is_remote:
            cleanup_temp_folder(Path(repo_path))


async def scan_repo_logic_async(request: ScanRequest, task_id: str):
    try:
        update_task(task_id, TaskStatus.RUNNING)
        result = await perform_scan(request)
        result_dict = result.dict()
        result_dict["__cleanup_path"] = result.output_dir
        result_dict["__timestamp"] = time.time()
        update_task(task_id, TaskStatus.COMPLETED, result=result_dict)
    except Exception as e:
        update_task(task_id, TaskStatus.FAILED, error=str(e))
