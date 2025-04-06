import uuid
import os
from pathlib import Path
from gittxt.core.scanner import scan_repo
from gittxt.core.output_builder import build_outputs
from gittxt.core.repository import download_and_extract_repo

BASE_OUTPUT_DIR = "outputs"

def run_gittxt_scan(repo_url: str, options: dict):
    """
    Full scan: runs scan + builds output files.
    Returns scan_id, summary, and file paths.
    """
    scan_id = str(uuid.uuid4())
    output_dir = Path(BASE_OUTPUT_DIR) / scan_id
    output_dir.mkdir(parents=True, exist_ok=True)

    repo_path, repo_meta = download_and_extract_repo(
        repo_url,
        branch=options.get("branch"),
        subdir=options.get("subdir")
    )

    scan_result = scan_repo(
        repo_path=repo_path,
        output_dir=str(output_dir),
        subdir=options.get("subdir"),
        include_patterns=options.get("include_patterns"),
        exclude_patterns=options.get("exclude_patterns"),
        exclude_dirs=options.get("exclude_dirs"),
        size_limit=options.get("size_limit"),
        tree_depth=options.get("tree_depth"),
        lite=options.get("lite", False),
        non_interactive=True
    )

    output_files = build_outputs(
        scan_result=scan_result,
        output_dir=str(output_dir),
        to_txt=True,
        to_md=True,
        to_json=True,
        to_zip=True
    )

    return {
        "scan_id": scan_id,
        "repo_name": repo_meta["name"],
        "branch": repo_meta["branch"],
        "outputs": output_files,
        "summary": scan_result["summary"]
    }

def run_gittxt_inspect(repo_url: str, branch: str = None, subdir: str = None):
    """
    Lightweight repo inspection without output file generation.
    """
    repo_path, repo_meta = download_and_extract_repo(
        repo_url, branch=branch, subdir=subdir
    )

    scan_result = scan_repo(
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
