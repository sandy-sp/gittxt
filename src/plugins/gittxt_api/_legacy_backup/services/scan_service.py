from uuid import uuid4
from pathlib import Path

from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.file_utils import load_gittxtignore
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT
from plugins.gittxt_api.dependencies import OUTPUT_DIR
from plugins.gittxt_api.models.scan_models import ScanRequest, ScanResponse

# If you want to show summary data in the response, you can import:
from gittxt.utils.summary_utils import generate_summary

async def perform_scan(request: ScanRequest) -> ScanResponse:
    scan_id = str(uuid4())
    scan_output_dir = OUTPUT_DIR / scan_id
    scan_output_dir.mkdir(parents=True, exist_ok=True)

    # 1) Resolve repository
    handler = RepositoryHandler(source=request.repo_path, branch=request.branch)
    await handler.resolve()
    local_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()

    # 2) Build excludes
    merged_excludes = set(EXCLUDED_DIRS_DEFAULT) | set(request.exclude_dirs)

    # If sync_ignore => load .gittxtignore patterns
    if request.sync_ignore:
        dynamic_ignores = load_gittxtignore(Path(local_path))
        merged_excludes |= set(dynamic_ignores)

    # 3) If docs_only => default include to **/*.md unless user provided patterns
    if request.docs_only and not request.include_patterns:
        include_patterns = ["**/*.md"]
    else:
        include_patterns = request.include_patterns

    # 4) Prepare Scanner
    target_root = Path(local_path) / subdir if subdir else Path(local_path)
    scanner = Scanner(
        root_path=target_root,
        exclude_dirs=list(merged_excludes),
        include_patterns=include_patterns,
        exclude_patterns=request.exclude_patterns,
        size_limit=request.size_limit,        # new field
    )

    # 5) Run scan
    textual_files, non_textual_files = await scanner.scan_directory()

    # 6) Build outputs
    mode = "lite" if request.lite else "rich"
    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=scan_output_dir,
        output_format="txt,json,md",   # or adapt to user choice
        repo_url=request.repo_path if is_remote else None,
        branch=used_branch,
        subdir=subdir,
        mode=mode
    )

    await builder.generate_output(
        textual_files,
        non_textual_files,
        repo_path=target_root,
        create_zip=request.create_zip,
        tree_depth=request.tree_depth,
        skip_tree=request.skip_tree
    )

    # (Optional) If you want a summary in the response, compute it:
    # Note: If you prefer to keep it minimal, skip this.
    summary_data = await generate_summary(textual_files + non_textual_files)

    # 7) Cleanup if remote
    if is_remote:
        cleanup_temp_folder(Path(local_path))

    # 8) Return a result
    return ScanResponse(
        scan_id=scan_id,
        repo_name=repo_name,
        num_textual_files=len(textual_files),
        num_non_textual_files=len(non_textual_files),
        artifact_dir=str(scan_output_dir),
        message="Scan completed",
        summary=summary_data
    )
