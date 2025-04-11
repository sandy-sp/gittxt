import shutil
from pathlib import Path
from gittxt.core.repository import RepositoryHandler
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder
from gittxt.utils.subcat_utils import detect_subcategory
from gittxt.utils.tree_utils import generate_tree

PLUGIN_OUTPUT_DIR = Path("/tmp/gittxt_plugin_output")


def load_repository_summary(github_url: str) -> dict:
    """
    Clone and analyze the GitHub repo to return:
    - repo_name
    - total files
    - token count
    - directory tree
    - file types (textual/non-textual)
    """
    PLUGIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    downloader = RepositoryHandler(github_url, output_dir=PLUGIN_OUTPUT_DIR)
    repo_path = downloader.download()

    scanner = Scanner(repo_path)
    summary = scanner.get_summary_metadata()
    dir_tree = generate_tree(repo_path)

    textual, non_textual = detect_subcategory()

    return {
        "repo_name": repo_path.name,
        "repo_path": str(repo_path),
        "summary": summary,
        "dir_tree": dir_tree,
        "textual_types": textual,
        "non_textual_types": non_textual,
        "scanner": scanner,
    }


def execute_scan_with_filters(github_url: str, filters: dict) -> dict:
    """
    Run the full scan using Scanner + OutputBuilder with user filters.
    """
    repo_path = Path(filters.get("repo_path"))
    scanner: Scanner = filters.get("scanner")

    # Apply filters dynamically
    scan_result = scanner.scan(
        include_patterns=filters.get("include_patterns"),
        exclude_patterns=filters.get("exclude_patterns"),
        exclude_dirs=filters.get("exclude_dirs"),
        custom_textual_types=filters.get("custom_textual"),
        size_limit=filters.get("size_limit"),
        lite=filters.get("lite_mode", False)
    )

    output_formats = filters.get("output_formats", ["txt"])
    zip_output = filters.get("zip_output", False)

    builder = OutputBuilder(scan_result, output_dir=PLUGIN_OUTPUT_DIR)
    paths = builder.generate_outputs(formats=output_formats)

    if zip_output:
        zip_path = builder.bundle_outputs()
        paths["zip"] = zip_path

    return paths


def cleanup_output_dir():
    if PLUGIN_OUTPUT_DIR.exists():
        shutil.rmtree(PLUGIN_OUTPUT_DIR)
        PLUGIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
