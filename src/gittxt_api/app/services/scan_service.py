import os
import tempfile
import shutil
from typing import Optional
from app.models.request import ScanRequest
from app.models.response import (
    ScanResponse, ScanSummary, FileMetadata, TreeNode
)
from app.core.gittxt_runner import run_gittxt_scan
from app.utils.tree_utils import build_tree_from_path
from app.services.zip_utils import generate_download_links
from app.utils.json_loader import load_json

async def run_scan_job(request: ScanRequest, scan_id: str) -> Optional[ScanResponse]:
    try:
        # 1. Create a temp working directory for this scan
        work_dir = tempfile.mkdtemp(prefix=f"scan_{scan_id}_")

        # 2. Run the actual scan using the CLI-wrapped core
        output_dir = os.path.join(work_dir, "output")
        run_gittxt_scan(request, output_dir)

        # 3. Load outputs
        summary_data = load_json(os.path.join(output_dir, "summary.json"))
        manifest_data = load_json(os.path.join(output_dir, "manifest.json"))
        subcat_data = load_json(os.path.join(output_dir, "file_subcategories.json"))

        # 4. Build response objects
        summary = ScanSummary(
            file_count=summary_data.get("file_count", 0),
            token_count=summary_data.get("token_count", 0),
            language_breakdown=summary_data.get("language_breakdown", {})
        )

        metadata = [
            FileMetadata(
                path=item["path"],
                type=item.get("type", "unknown"),
                size_kb=item.get("size_kb", 0),
                token_count=item.get("token_count", 0)
            )
            for item in manifest_data.get("files", [])
        ]

        tree = build_tree_from_path(output_dir, max_depth=request.tree_depth or 3)

        download_links = generate_download_links(scan_id, request.output_formats, request.zip)

        return ScanResponse(
            scan_id=scan_id,
            summary=summary,
            tree=tree,
            file_metadata=metadata,
            subcategory_breakdown=subcat_data,
            download_links=download_links
        )

    except Exception as e:
        print(f"[ERROR] Scan job failed: {e}")
        return None

    finally:
        # Optional: clean up temp files if not zipping
        if not request.zip:
            shutil.rmtree(work_dir, ignore_errors=True)
