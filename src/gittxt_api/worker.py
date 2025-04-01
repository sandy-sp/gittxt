import os
from .models import ScanRequest, ScanResponse
from .utils import generate_scan_id
from .config import API_TMP_DIR

from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.tree_formatter import TreeFormatter
from gittxt.utils.summary_utils import SummaryBuilder

def run_scan(req: ScanRequest) -> ScanResponse:
    scan_id = generate_scan_id()
    work_dir = os.path.join(API_TMP_DIR, scan_id)
    os.makedirs(work_dir, exist_ok=True)

    repo = RepositoryHandler(repo_url=req.repo_url, branch=req.branch, subdir=req.subdir)
    repo.download()

    scanner = Scanner(
        repo_path=repo.repo_path,
        include_patterns=req.include_patterns,
        exclude_patterns=req.exclude_patterns,
        size_limit=req.size_limit,
    )
    files = scanner.scan()

    builder = OutputBuilder(
        output_dir=os.path.join(work_dir, "outputs"),
        repo_name=repo.repo_name,
        output_format=req.output_format,
        lite_mode=req.lite,
        zip_output="zip" in req.output_format
    )
    builder.build(files)

    summary = SummaryBuilder(files).build()
    tree = TreeFormatter().build(repo.repo_path, depth=None)

    return ScanResponse(
        scan_id=scan_id,
        summary=summary,
        directory_tree=tree,
        file_types=summary.get("file_types", {})
    )
