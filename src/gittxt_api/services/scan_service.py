import tempfile
import asyncio
from gittxt.core.scanner import Scanner
from gittxt.core.config import GittxtConfig
from gittxt_api.models.scan import ScanRequest
from gittxt_api.utils.logger import get_logger

logger = get_logger("scan_service")

async def scan_repo_logic(request: ScanRequest) -> dict:
    temp_dir = tempfile.mkdtemp()
    try:
        # Create config for Gittxt Scanner
        config = GittxtConfig(
            output_dir=temp_dir,
            output_format=request.output_format,
            zip=request.zip,
            lite=request.lite,
            branch=request.branch,
        )

        scanner = Scanner(config=config)

        # Run scan in a thread-safe async way
        result = await asyncio.to_thread(scanner.scan, request.repo_url)

        return {
            "message": "Scan completed successfully",
            "output_dir": temp_dir,
            "summary": result.summary,
            "manifest": result.manifest,
        }

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise
