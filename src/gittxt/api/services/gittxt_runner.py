import uuid
import os
from pathlib import Path
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.core.repository import RepositoryHandler
from gittxt.utils.tree_utils import generate_tree
from gittxt import OUTPUT_DIR

BASE_OUTPUT_DIR = "outputs"

async def run_gittxt_scan(
    repo_path: Path,
    scan_id: str,
    lite: bool = False
) -> dict:
    """
    Run a full Gittxt scan on a local path.

    Args:
        repo_path (Path): Path to the repository root
        scan_id (str): Unique identifier for the scan session
        lite (bool): If True, generates lite outputs only

    Returns:
        dict: scan summary including files, tree, and output directory
    """
    output_dir = OUTPUT_DIR / scan_id / "artifacts"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Scan repository
    scanner = Scanner(
        root_path=repo_path,
        progress=False
    )
    textual_files, non_textual_files = await scanner.scan_directory()

    # Generate outputs
    builder = OutputBuilder(
        repo_name=repo_path.name,
        output_dir=output_dir,
        output_format="txt,json,md",
        repo_path=repo_path,
        mode="lite" if lite else "rich"
    )
    await builder.generate_output(
        textual_files=textual_files,
        non_textual_files=non_textual_files,
        repo_path=repo_path
    )

    # Generate directory tree
    tree = generate_tree(repo_path)

    return {
        "scan_id": scan_id,
        "repo_name": repo_path.name,
        "textual_files": [str(f.relative_to(repo_path)) for f in textual_files],
        "non_textual_files": [str(f.relative_to(repo_path)) for f in non_textual_files],
        "tree": tree,
        "output_dir": str(output_dir),
    }

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
