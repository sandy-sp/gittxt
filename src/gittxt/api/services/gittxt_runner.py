import uuid
import os
from pathlib import Path
from fastapi import BackgroundTasks
from typing import Optional, List, Dict, Any, Union
import asyncio
import tempfile

from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.core.repository import RepositoryHandler
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.core.logger import Logger
from gittxt import OUTPUT_DIR
from gittxt.core.config import ConfigManager  # Ensure this import exists
from gittxt.api.schemas.summary import SummaryResponse

# Initialize logger at the module level
logger = Logger.get_logger(__name__)

# Load global config
config = ConfigManager.load_config()

class GittxtRunnerError(Exception):
    """Exception raised for errors in the GittxtRunner."""
    pass

async def _perform_actual_scan(scan_id: str, repo_url: str, config: dict, options: dict):
    try:
        logger.info("Initiating repository handling...")
        repo_handler = RepositoryHandler(
            source=repo_url,
            branch=options.get('branch'),
        )
        await repo_handler.resolve()
        repo_path, subdir_in_repo, is_remote, repo_name, used_branch = repo_handler.get_local_path()
        logger.info(f"Repository resolved: {repo_name}, Branch: {used_branch}, Path: {repo_path}")

        scan_root = Path(repo_path)
        if options.get('subdir'):
            scan_root = scan_root / options['subdir']
            if not scan_root.exists() or not scan_root.is_dir():
                raise GittxtRunnerError(f"Subdirectory '{options['subdir']}' not found in repository.", status_code=404)
            logger.info(f"Scanning subdirectory: {options['subdir']}")

        # Scanner setup
        logger.debug("Configuring scanner...")
        default_excludes = set(config.get("filters", {}).get("excluded_dirs", []))
        request_excludes = set(options.get('exclude_dirs') or [])
        merged_exclude_dirs = list(default_excludes | request_excludes)

        scanner = Scanner(
            root_path=scan_root,
            exclude_dirs=merged_exclude_dirs,
            size_limit=options.get('size_limit'),
            include_patterns=options.get('include_patterns'),
            exclude_patterns=options.get('exclude_patterns'),
            use_ignore_file=options.get('use_sync', False),
            progress=False
        )

        logger.info("Scanning directory...")
        textual_files, non_textual_files = await scanner.scan_directory()
        skipped_files = scanner.skipped_files
        logger.info(f"Scan complete: {len(textual_files)} textual, {len(non_textual_files)} non-textual files found.")

        # Output builder setup
        scan_output_dir = OUTPUT_DIR / scan_id
        scan_output_dir.mkdir(parents=True, exist_ok=True)
        core_output_formats = options.get('output_formats') or config.get('output_formats', ['txt'])
        if core_output_formats:
            update_status(f"Configuring output builder for formats: {core_output_formats}...")
            builder = OutputBuilder(
                repo_name=repo_name,
                output_dir=scan_output_dir,
                output_format=",".join(core_output_formats),
                repo_url=repo_url if is_remote else None,
                branch=used_branch,
                subdir=options.get('subdir'),
                mode='lite' if options.get('lite_mode') else 'rich',
            )
            await builder.generate_output(
                textual_files=textual_files,
                non_textual_files=non_textual_files,
                repo_root_path=Path(repo_path),
                create_zip='zip' in core_output_formats,
                tree_depth=options.get('tree_depth'),
            )
            update_status("Output file generation complete.")

        # Generate summary
        if textual_files or non_textual_files:
            update_status("Generating summary data...")
            summary_data = await generate_summary(textual_files + non_textual_files)
            summary_file = scan_output_dir / "summary.json"
            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(summary_data, f, indent=2)
            update_status(f"Summary data saved to {summary_file.name}")

    except Exception as e:
        logger.error(f"Unhandled Exception during scan: {e}", exc_info=True)
    finally:
        if is_remote and repo_handler and repo_path:
            logger.info(f"Cleaning up temporary clone directory: {repo_path}")
            cleanup_temp_folder(Path(repo_path))
        logger.info("Background task finished.")

async def run_gittxt_scan(
    repo_url: str,
    branch: Optional[str] = None,
    output_formats: List[str] = None,
    lite_mode: bool = False,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    exclude_dirs: Optional[List[str]] = None,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Run a Gittxt scan as a background task and return outputs.
    
    Args:
        repo_url: URL of the GitHub repository to scan
        branch: Git branch to scan (defaults to main/master)
        output_formats: List of output formats to generate
        lite_mode: Whether to use lite mode (file list only)
        include_patterns: Glob patterns to include
        exclude_patterns: Glob patterns to exclude
        exclude_dirs: Directories to exclude
        output_dir: Custom output directory
        
    Returns:
        Dictionary with scan results
    """
    repo_path = None
    
    try:
        logger.info(f"Starting scan of repository: {repo_url}")
        repo_handler = RepositoryHandler(
            repo_url=repo_url,
            branch=branch
        )
        
        repo_path = await repo_handler.clone_repository()
        repo_name = Path(repo_path).name
        logger.debug(f"Cloned repository to {repo_path}")
        
        # Initialize scanner
        scanner = Scanner(
            repo_paths=[repo_path],
            output_dir=str(output_dir) if output_dir else None,
            include_patterns=include_patterns or config.get('include_patterns', []),
            exclude_patterns=exclude_patterns or config.get('exclude_patterns', []),
            exclude_dirs=exclude_dirs or config.get("filters", {}).get("excluded_dirs", []),
            lite_mode=lite_mode
        )
        
        # Scan files
        textual_files, non_textual_files = await scanner.scan_directories()
        logger.info(f"Scan found {len(textual_files)} textual files and {len(non_textual_files)} non-textual files")
        
        # Build outputs
        scan_output_dir = OUTPUT_DIR / str(uuid.uuid4())
        scan_output_dir.mkdir(parents=True, exist_ok=True)
        builder = OutputBuilder(
            output_formats=output_formats or config.get('output_formats', ['txt']),
            repo_name=repo_name,
            output_dir=scan_output_dir,
            repo_url=repo_url,
            branch=branch,
            mode="lite" if lite_mode else "rich"
        )
        
        outputs = builder.process_files(textual_files, non_textual_files)
        logger.info(f"Generated outputs: {', '.join(output_formats)}")
        
        return {
            "repo_name": repo_name,
            "textual_files": len(textual_files),
            "non_textual_files": len(non_textual_files),
            "outputs": outputs
        }
    
    except Exception as e:
        logger.error(f"Scan failed: {str(e)}", exc_info=True)
        raise GittxtRunnerError(f"Scan failed: {str(e)}")
        
    finally:
        if repo_path and Path(repo_path).exists():
            logger.info(f"Cleaning up temporary directory: {repo_path}")
            cleanup_temp_folder(Path(repo_path))

async def get_gittxt_summary(scan_id: str) -> SummaryResponse:
    logger.debug(f"Attempting to retrieve summary for scan_id: {scan_id}")
    try:
        config = ConfigManager.load_config()
        output_dir_base = Path(config.get("output_dir", "./gittxt_output"))
        scan_output_dir = output_dir_base / scan_id
        summary_file = scan_output_dir / "summary.json"
        status_file = scan_output_dir / "status.log"

        if not scan_output_dir.exists():
            raise GittxtRunnerError(f"Scan ID '{scan_id}' output directory not found.", status_code=404)

        if status_file.exists():
            status_content = status_file.read_text(encoding="utf-8")
            if "Scan completed successfully." not in status_content:
                if "Error" in status_content:
                    raise GittxtRunnerError(f"Scan '{scan_id}' failed. Check status.log for details.", status_code=409)
                else:
                    raise GittxtRunnerError(f"Scan '{scan_id}' is still in progress.", status_code=202)

        if not summary_file.exists():
            raise GittxtRunnerError(f"Summary file not found for scan '{scan_id}'.", status_code=404)

        with summary_file.open("r", encoding="utf-8") as f:
            summary_data = json.load(f)

        formatted_summary = summary_data.get("formatted", {})
        tokens_by_type_fmt = formatted_summary.get("tokens_by_type", {})
        file_breakdown_raw = summary_data.get("file_type_breakdown", {})

        breakdown_list = [
            FileBreakdown(
                file_type=type_name,
                count=count,
                estimated_tokens_formatted=tokens_by_type_fmt.get(type_name, f"{summary_data.get('tokens_by_type', {}).get(type_name, 0):,}")
            )
            for type_name, count in file_breakdown_raw.items()
        ]

        return SummaryResponse(
            scan_id=scan_id,
            repo_name=summary_data.get("repo_name", "Unknown"),
            total_files=summary_data.get("total_files", 0),
            total_size_bytes=summary_data.get("total_size", 0),
            total_size_formatted=formatted_summary.get("total_size", "N/A"),
            estimated_tokens=summary_data.get("estimated_tokens", 0),
            estimated_tokens_formatted=formatted_summary.get("estimated_tokens", "N/A"),
            file_type_breakdown=breakdown_list
        )
    except Exception as e:
        logger.error(f"Unexpected error retrieving summary for {scan_id}: {e}", exc_info=True)
        raise GittxtRunnerError(f"Internal server error retrieving summary: {str(e)}", status_code=500)

def run_gittxt_inspect(repo_url: str, branch: str = None, subdir: str = None):
    """
    Lightweight repo inspection without output file generation.
    """
    repo_path, repo_meta = RepositoryHandler(
        repo_url, branch=branch, subdir=subdir
    )

    scan_result = Scanner(
        repo_path=repo_path,
        output_dir=None,
        subdir=subdir,
        lite=False,
        non_interactive=True,
        inspect_only=True
    )

    return {
        "repo_name": repo_meta["name"],
        "branch": repo_meta["branch"],
        "tree": scan_result.get("tree", []),
        "textual_files": scan_result.get("textual_files", []),
        "non_textual_files": scan_result.get("non_textual_files", []),
        "summary": scan_result.get("summary", {}),
        "preview_snippets": scan_result.get("preview_snippets", [])
    }
