import shutil
from uuid import uuid4
from pathlib import Path

from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.utils.file_utils import load_gittxtignore
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT
from gittxt.utils.tree_utils import generate_tree

from plugins.gittxt_api.api.v1.models.inspect_models import InspectRequest, InspectResponse, FileInfo
from plugins.gittxt_api.api.v1.deps import get_output_dir

async def perform_inspect(request: InspectRequest) -> InspectResponse:
    scan_id = str(uuid4())
    output_dir = get_output_dir()
    temp_dir = output_dir / scan_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    handler = RepositoryHandler(source=request.repo_path, branch=request.branch)
    await handler.resolve()
    local_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()
    root_path = Path(local_path) / subdir if subdir else Path(local_path)

    merged_excludes = set(EXCLUDED_DIRS_DEFAULT) | set(request.exclude_dirs)
    merged_excludes |= set(load_gittxtignore(root_path))

    tree_str = generate_tree(root_path, max_depth=request.max_depth)

    scanner = Scanner(
        root_path=root_path,
        exclude_dirs=list(merged_excludes)
    )
    textual_files, non_textual_files = await scanner.scan_directory()

    def file_info_list(paths):
        return [
            FileInfo(
                path=p.relative_to(root_path).as_posix(),
                size=p.stat().st_size,
                ext=p.suffix.lower()
            )
            for p in paths
        ]

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)
    if is_remote:
        cleanup_temp_folder(Path(local_path))

    return InspectResponse(
        scan_id=scan_id,
        repo_name=repo_name,
        branch=used_branch,
        repo_tree=tree_str,
        textual_files=file_info_list(textual_files),
        non_textual_files=file_info_list(non_textual_files),
    )
