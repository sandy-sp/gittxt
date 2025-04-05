import os
from gittxt.core.scanner import Scanner
from gittxt.core.config import ConfigManager
from gittxt.core.output_builder import OutputBuilder
from gittxt.core.repository import RepoHandler


def run_gittxt_scan(request, output_dir: str) -> None:
    # Step 1: Prepare repo (clone if remote)
    repo_path = RepoHandler.get_repo(
        url=request.repo_url,
        branch=request.branch,
        subdir=request.subdir
    )

    # Step 2: Setup config
    config = ConfigManager(
        output_dir=output_dir,
        output_formats=request.output_formats,
        exclude_dirs=request.exclude_dirs,
        include_patterns=request.include_patterns,
        exclude_patterns=request.exclude_patterns,
        size_limit=request.size_limit_kb * 1024,  # Convert KB to bytes
        use_gittxtignore=request.sync,
        tree_depth=request.tree_depth,
        lite=request.lite,
        zip_output=request.zip
    )

    # Step 3: Build outputs
    output_builder = OutputBuilder(config=config)
    Scanner.scan_repo(
        repo_path=repo_path,
        config=config,
        output_builder=output_builder
    )

    # Step 4: Cleanup repo cache if needed (optional)
    if repo_path and os.path.isdir(repo_path) and not request.repo_url.startswith("file://"):
        RepoHandler.cleanup_repo(repo_path)
