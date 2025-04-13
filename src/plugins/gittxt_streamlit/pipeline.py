import shutil
import asyncio
from pathlib import Path
from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.summary_utils import generate_summary
from gittxt.utils.file_utils import load_gittxtignore
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT

PLUGIN_OUTPUT_DIR = Path("/tmp/gittxt_plugin_output")


def load_repository_summary(github_url: str, include_default_excludes: bool, include_gitignore: bool) -> dict:
    """
    Clone and analyze a GitHub repo or local path.
    Returns repo metadata including dir tree and file summary.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    handler = RepositoryHandler(source=github_url)
    repo_path = loop.run_until_complete(handler.resolve())
    repo_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()

    # Validate subdir path
    scan_root = Path(repo_path)
    if subdir:
        scan_root = scan_root / subdir
        if not scan_root.exists():
            raise FileNotFoundError(f"Subdirectory '{subdir}' does not exist in the repository.")

    # Merge .gitignore patterns if requested
    dynamic_ignores = load_gittxtignore(scan_root) if include_gitignore else []
    merged_excludes = list(set(EXCLUDED_DIRS_DEFAULT if include_default_excludes else []) | set(dynamic_ignores))

    scanner = Scanner(
        root_path=scan_root,
        exclude_dirs=merged_excludes,
        size_limit=None,
        include_patterns=[],
        exclude_patterns=[],
        progress=False,
        use_ignore_file=include_gitignore,
    )

    textual_files, non_textual_files = loop.run_until_complete(scanner.scan_directory())
    tree_summary = generate_tree(scan_root)
    summary_data = loop.run_until_complete(generate_summary(textual_files + non_textual_files))

    return {
        "repo_name": repo_name,
        "repo_path": str(scan_root),
        "tree_summary": tree_summary,
        "summary": summary_data,
        "textual_files": textual_files,
        "non_textual_files": non_textual_files,
        "handler": handler,
    }


def execute_scan_with_filters(github_url: str, filters: dict) -> dict:
    """
    Run a filtered scan using Gittxt core logic and return output paths.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    repo_path = Path(filters.get("repo_path"))
    textual_files = filters.get("textual_files", [])
    non_textual_files = filters.get("non_textual_files", [])
    repo_name = filters.get("repo_name")
    handler: RepositoryHandler = filters.get("handler")
    subdir = handler.subdir
    branch = handler.branch
    repo_url = github_url

    output_formats = filters.get("output_formats", ["txt"])
    output_dir = PLUGIN_OUTPUT_DIR
    mode = "lite" if filters.get("lite_mode") else "rich"

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=output_dir,
        output_format=output_formats,
        repo_url=repo_url,
        branch=branch,
        subdir=subdir,
        mode=mode,
    )

    output_paths = loop.run_until_complete(
        builder.generate_output(
            textual_files,
            non_textual_files,
            repo_path,
            create_zip=filters.get("zip_output", False),
            tree_depth=filters.get("tree_depth"),
        )
    )
    return {path.suffix.lstrip("."): str(path) for path in output_paths if path}


def cleanup_output_dir():
    if PLUGIN_OUTPUT_DIR.exists():
        shutil.rmtree(PLUGIN_OUTPUT_DIR)
    PLUGIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
