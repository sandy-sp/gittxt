from uuid import uuid4
from pathlib import Path
from fastapi import HTTPException
from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.file_utils import load_gittxtignore, sanitize_path
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT
from gittxt.utils.summary_utils import generate_summary
from plugins.gittxt_api.api.v1.models.scan_models import ScanRequest, ScanResponse
from plugins.gittxt_api.api.v1.deps import get_output_dir


async def perform_scan(request: ScanRequest) -> ScanResponse:
    try:
        # Sanitize repository path
        sanitized_repo_path = sanitize_path(request.repo_path)
        if not sanitized_repo_path:
            raise HTTPException(status_code=400, detail="Invalid repository path.")

        scan_id = str(uuid4())
        output_dir = get_output_dir()
        scan_output_dir = output_dir / scan_id
        scan_output_dir.mkdir(parents=True, exist_ok=True)

        handler = RepositoryHandler(source=sanitized_repo_path, branch=request.branch)
        await handler.resolve()
        local_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()
        scan_root = Path(local_path) / subdir if subdir else Path(local_path)

        # Validate repository path
        if not scan_root.exists():
            raise HTTPException(status_code=400, detail="Repository path does not exist.")

        # 2. Merge excludes
        merged_excludes = set(EXCLUDED_DIRS_DEFAULT) | set(request.exclude_dirs)
        if request.sync_ignore:
            try:
                merged_excludes |= set(load_gittxtignore(scan_root))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to load .gittxtignore: {str(e)}")

        # 3. Include patterns for docs_only mode
        include_patterns = request.include_patterns or (["**/*.md"] if request.docs_only else [])

        # Scan repository
        try:
            scanner = Scanner(
                root_path=scan_root,
                exclude_dirs=list(merged_excludes),
                include_patterns=include_patterns,
                exclude_patterns=request.exclude_patterns,
                size_limit=request.size_limit
            )
            textual_files, non_textual_files = await scanner.scan_directory()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scanning failed: {str(e)}")

        # Generate outputs
        mode = "lite" if request.lite else "rich"
        try:
            builder = OutputBuilder(
                repo_name=repo_name,
                output_dir=scan_output_dir,
                output_format="txt,json,md",
                repo_url=request.repo_path if is_remote else None,
                branch=used_branch,
                subdir=subdir,
                mode=mode
            )
            await builder.generate_output(
                textual_files,
                non_textual_files,
                repo_path=scan_root,
                create_zip=request.create_zip,
                tree_depth=request.tree_depth,
                skip_tree=request.skip_tree
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Output generation failed: {str(e)}")

        # 6. Generate summary
        summary_data = await generate_summary(textual_files + non_textual_files)

        # 7. Cleanup if remote
        if is_remote:
            cleanup_temp_folder(Path(local_path))

        return ScanResponse(
            scan_id=scan_id,
            repo_name=repo_name,
            num_textual_files=len(textual_files),
            num_non_textual_files=len(non_textual_files),
            artifact_dir=str(scan_output_dir),
            message="Scan completed successfully.",
            summary=summary_data
        )

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
