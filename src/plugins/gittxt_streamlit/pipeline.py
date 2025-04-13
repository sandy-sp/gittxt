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
from .state_manager import get_output_dir


async def load_repository_summary(github_url: str, include_default_excludes: bool, include_gitignore: bool) -> dict:
    """
    Clone and analyze a GitHub repo or local path.
    Returns repo metadata including dir tree and file summary.
    """
    handler = RepositoryHandler(source=github_url)
    await handler.resolve()
    repo_path, subdir, is_remote, repo_name, used_branch = handler.get_local_path()

    scan_root = Path(repo_path)
    if subdir:
        scan_root = scan_root / subdir
        if not scan_root.exists():
            raise FileNotFoundError(f"Subdirectory '{subdir}' does not exist in the repository.")

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

    textual_files, non_textual_files = await scanner.scan_directory()
    tree_summary = generate_tree(scan_root)
    summary_data = await generate_summary(textual_files + non_textual_files)

    return {
        "repo_name": repo_name,
        "repo_path": str(scan_root),
        "tree_summary": tree_summary,
        "summary": summary_data,
        "textual_file_paths": [str(p) for p in textual_files],
        "non_textual_file_paths": [str(p) for p in non_textual_files],
        "branch": used_branch,
        "subdir": subdir,
        "repo_url": github_url,
    }


async def execute_scan_with_filters(filters: dict) -> dict:
    """
    Run a filtered scan using Gittxt core logic and return output paths.
    """
    repo_path = Path(filters.get("repo_path"))
    textual_files = [Path(p) for p in filters.get("textual_file_paths", [])]
    non_textual_files = [Path(p) for p in filters.get("non_textual_file_paths", [])]
    repo_name = filters.get("repo_name")
    repo_url = filters.get("repo_url")
    branch = filters.get("branch")
    subdir = filters.get("subdir")

    output_formats = filters.get("output_formats", ["txt"])
    output_dir = get_output_dir()
    mode = "lite" if filters.get("lite_mode") else "rich"
    create_zip = filters.get("zip_output", False)
    tree_depth = filters.get("tree_depth")

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=output_dir,
        output_format=output_formats,
        repo_url=repo_url,
        branch=branch,
        subdir=subdir,
        mode=mode,
    )

    output_paths = await builder.generate_output(
        textual_files,
        non_textual_files,
        repo_path,
        create_zip=create_zip,
        tree_depth=tree_depth,
    )

    return {path.suffix.lstrip("."): str(path) for path in output_paths if path and path.exists()}


def cleanup_output_dir():
    output_dir = get_output_dir()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
