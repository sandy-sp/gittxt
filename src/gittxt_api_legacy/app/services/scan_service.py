import os
import tempfile
import shutil
from typing import Optional
from gittxt_api.app.models.request import ScanRequest
from gittxt_api.app.models.response import (
    ScanResponse, ScanSummary, FileMetadata, TreeNode
)
from gittxt_api.app.core.gittxt_runner import run_gittxt_scan
from gittxt_api.app.utils.tree_utils import build_tree_from_path
from gittxt_api.app.services.zip_utils import generate_download_links
from gittxt_api.app.utils.json_loader import load_json

async def run_scan_job(request: ScanRequest, scan_id: str) -> Optional[ScanResponse]:
    try:
        # Standardized output directory
        output_dir = f"/tmp/scan_{scan_id}_output"

        # Run the actual scan using the CLI-wrapped core
        run_gittxt_scan(request, output_dir)

        # Load outputs
        summary_data = load_json(os.path.join(output_dir, "summary.json"))
        manifest_data = load_json(os.path.join(output_dir, "manifest.json"))
        subcat_data = load_json(os.path.join(output_dir, "file_subcategories.json"))

        # Build response objects
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
            for item in (manifest_data.get("files") or [])
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
            shutil.rmtree(output_dir, ignore_errors=True)
