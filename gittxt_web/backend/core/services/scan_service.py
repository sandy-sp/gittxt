from gittxt_web.backend.api.v1.models.scan_models import ScanRequest, ScanResponse
from gittxt.cli.cli_scan import perform_scan_from_api
from gittxt.core.logger import Logger

logger = Logger.get_logger(__name__)

async def perform_scan(req: ScanRequest) -> ScanResponse:
    """
    Orchestrates the scanning of a repository based on user request.
    This function acts as a bridge between the API model and the core CLI logic.
    """
    try:
        # Map the Pydantic model to the function arguments
        scan_results = await perform_scan_from_api(
            repos=[req.repo_url],
            exclude_dirs=req.exclude_dirs,
            size_limit=req.size_limit,
            branch=req.branch,
            output_dir=req.output_dir,
            output_format=",".join(req.output_formats),
            include_patterns=req.include_patterns,
            exclude_patterns=req.exclude_patterns,
            create_zip=req.create_zip,
            lite=req.lite,
            sync=req.sync,
            docs=req.docs,
            no_tree=req.no_tree
        )
        return ScanResponse(**scan_results)

    except Exception as e:
        logger.error(f"Scan service failed: {e}")
        # Re-raise the exception or handle it to return a proper HTTP error
        raise e