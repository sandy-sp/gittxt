from pathlib import Path
from fastapi import HTTPException
from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.file_utils import load_gittxtignore
from gittxt.utils.summary_utils import generate_summary
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT
from gittxt.utils.filetype_utils import FiletypeConfigManager
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt_api.models.scan_request import ScanRequest
from gittxt_api.models.scan_response import ScanResponse

import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger("gittxt_api")


async def perform_scan(scan_req: ScanRequest) -> ScanResponse:
    try:
        # Resolve repo (local or remote)
        handler = RepositoryHandler(
            source=scan_req.repo_url,
            branch=scan_req.branch,
        )
        await handler.resolve()
        repo_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()

        scan_root = Path(repo_path)
        if subdir:
            scan_root = scan_root / subdir

        # Merge exclude dirs
        dynamic_ignores = load_gittxtignore(scan_root) if scan_req.sync_ignore else []
        exclude_dirs = list(
            set(scan_req.exclude_dirs or [])
            | set(dynamic_ignores)
            | set(EXCLUDED_DIRS_DEFAULT)
        )

        # Warn if include-patterns target non-textual files
        for pattern in scan_req.include_patterns or []:
            ext = Path(pattern).suffix.lower()
            if ext and not FiletypeConfigManager.is_known_textual_ext(ext):
                logger.warning(f"Include pattern targets non-textual extension: {ext}")

        # Run scanner
        scanner = Scanner(
            root_path=scan_root,
            exclude_dirs=exclude_dirs,
            size_limit=scan_req.size_limit,
            include_patterns=scan_req.include_patterns,
            exclude_patterns=scan_req.exclude_patterns,
            progress=False,
            use_ignore_file=scan_req.sync_ignore,
        )
        textual_files, non_textual_files = await scanner.scan_directory()
        skipped_files = scanner.skipped_files

        if not textual_files:
            raise HTTPException(status_code=400, detail="No valid textual files found.")

        # Build output
        output_dir = Path(scan_req.output_dir).resolve()
        builder = OutputBuilder(
            repo_name=repo_name,
            output_dir=output_dir,
            output_format=scan_req.output_format,
            repo_url=scan_req.repo_url if is_remote else None,
            branch=used_branch,
            subdir=subdir,
            mode="lite" if scan_req.lite_mode else "rich",
        )
        output_files = await builder.generate_output(
            textual_files,
            non_textual_files,
            repo_path,
            create_zip=scan_req.create_zip,
            tree_depth=scan_req.tree_depth,
        )

        # Generate summary
        summary = await generate_summary(textual_files + non_textual_files)

        # Package response
        return ScanResponse(
            repo_name=repo_name,
            output_dir=str(output_dir),
            output_files=[str(p) for p in output_files],
            total_files=summary.get("total_files"),
            total_size_bytes=summary.get("total_size"),
            estimated_tokens=summary.get("estimated_tokens"),
            file_type_breakdown=summary.get("file_type_breakdown"),
            tokens_by_type=summary.get("tokens_by_type"),
            skipped_files=[(str(p), reason) for p, reason in skipped_files],
        )

    finally:
        if is_remote:
            cleanup_temp_folder(Path(repo_path))
