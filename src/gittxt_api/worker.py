import os
from datetime import datetime
from .models import ScanRequest, ScanResponse
from .utils import generate_scan_id
from .config import API_TMP_DIR

from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.summary_utils import generate_summary


def run_scan(req: ScanRequest) -> ScanResponse:
    scan_id = generate_scan_id()
    timestamp = datetime.utcnow().isoformat()
    work_dir = os.path.join(API_TMP_DIR, scan_id)
    os.makedirs(work_dir, exist_ok=True)

    # Clone GitHub repository to local path
    repo_handler = RepositoryHandler(
        source=req.repo_url,
        branch=req.branch,
        subdir=req.subdir
    )
    repo_handler.download()

    # Run scanner
    scanner = Scanner(
        repo_path=repo_handler.repo_path,
        include_patterns=req.include_patterns,
        exclude_patterns=req.exclude_patterns,
        size_limit=req.size_limit,
        include_all_supported=True,
        apply_ignore_file=True
    )
    scanned_files = scanner.scan()

    # Build outputs (text, json, markdown, zip, etc.)
    builder = OutputBuilder(
        repo_name=repo_handler.repo_name,
        output_dir=os.path.join(work_dir, "outputs"),
        output_format=req.output_format,
        lite_mode=req.lite,
        zip_output="zip" in req.output_format,
        scan_id=scan_id
    )
    builder.build(scanned_files)

    # Generate summary and directory tree
    summary = generate_summary(scanned_files)
    tree = generate_tree(repo_handler.repo_path)

    return ScanResponse(
        scan_id=scan_id,
        repo_name=repo_handler.repo_name,
        timestamp=timestamp,
        summary=summary,
        directory_tree=tree,
        file_types=summary.get("file_types", {})
    )
