# src/plugins/gittxt_streamlit/pipeline.py

import asyncio
from pathlib import Path
from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.cleanup_utils import cleanup_temp_folder
from gittxt.utils.summary_utils import generate_summary
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT
from gittxt.utils.file_utils import load_gittxtignore
from gittxt.utils.filetype_utils import FiletypeConfigManager
import logging


async def full_cli_equivalent_scan(repo_url: str, filters: dict) -> dict:
    """
    Replicates full `gittxt scan` CLI logic in Streamlit context.
    """
    branch = filters.get("branch")
    subdir = filters.get("subdir")
    docs_only = filters.get("docs_only", False)
    exclude_patterns = filters.get("exclude_patterns", [])
    exclude_dirs = filters.get("exclude_dirs", [])
    size_limit = filters.get("size_limit")
    output_formats = filters.get("output_formats", ["txt"])
    output_dir = Path(filters.get("output_dir", "/tmp/gittxt_streamlit_output"))
    mode = "lite" if filters.get("lite") else "rich"
    create_zip = filters.get("zip", False)
    tree_depth = filters.get("tree_depth")
    skip_tree = filters.get("skip_tree", False)
    sync_ignore = filters.get("sync", False)

    # Set include patterns based on docs_only
    if docs_only:
        include_patterns = ["**/*.md"]
    else:
        include_patterns = filters.get("include_patterns", [])

    handler = RepositoryHandler(repo_url, branch=branch, subdir=subdir)
    await handler.resolve()
    repo_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()

    scan_root = Path(repo_path)
    if subdir:
        scan_root = scan_root / subdir

    # .gittxtignore support
    dynamic_ignores = load_gittxtignore(scan_root) if sync_ignore else []
    merged_excludes = list(set(exclude_dirs + dynamic_ignores + EXCLUDED_DIRS_DEFAULT))

    for pattern in include_patterns:
        ext = Path(pattern).suffix.lower()
        if ext and not FiletypeConfigManager.is_known_textual_ext(ext):
            logging.warning(f"⚠️ Include pattern {pattern} may target non-textual files.")

    scanner = Scanner(
        root_path=scan_root,
        exclude_dirs=merged_excludes,
        size_limit=size_limit,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        use_ignore_file=sync_ignore,
        progress=False
    )

    textual_files, non_textual_files = await scanner.scan_directory()
    skipped = scanner.skipped_files

    if not textual_files:
        return {"error": "No valid textual files found.", "skipped": skipped}

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=output_dir,
        output_format=output_formats,
        repo_url=repo_url if is_remote else None,
        branch=used_branch,
        subdir=subdir,
        mode=mode,
    )

    output_files = await builder.generate_output(
        textual_files,
        non_textual_files,
        Path(repo_path),
        create_zip=create_zip,
        tree_depth=tree_depth,
        skip_tree=skip_tree,
    )

    summary = await generate_summary(textual_files + non_textual_files)
    result = {
        "repo_name": repo_name,
        "branch": used_branch,
        "subdir": subdir,
        "output_dir": str(output_dir),
        "output_files": output_files,
        "summary": summary,
        "skipped": skipped,
        "non_textual": non_textual_files,
    }

    if is_remote:
        cleanup_temp_folder(Path(repo_path))

    return result
