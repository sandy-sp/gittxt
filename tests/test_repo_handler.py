import pytest
from gittxt.core.repository import RepositoryHandler
from pathlib import Path

def test_local_repo_path_resolution():
    handler = RepositoryHandler()
    repo_path = handler.get_local_path("test_repo")
    assert repo_path.exists()
    assert (repo_path / "README.md").exists()

def test_invalid_repo_path_raises():
    handler = RepositoryHandler()
    with pytest.raises(FileNotFoundError):
        handler.get_local_path("non_existent_folder")

@pytest.mark.asyncio
async def test_invalid_github_repo_clone():
    handler = RepositoryHandler()
    with pytest.raises(RuntimeError):
        await handler.get_local_path_from_github("https://github.com/invalid/repo", branch="main")

@pytest.mark.asyncio
async def test_subdir_scan_resolution(tmp_path):
    handler = RepositoryHandler()
    repo_url = "https://github.com/sandy-sp/gittxt"
    subdir = "src/gittxt"
    branch = "main"

    # Clone the full repo, then resolve subdir
    full_path = await handler.get_local_path_from_github(repo_url, branch=branch, subdir=subdir, cache_dir=tmp_path)
    assert full_path.exists()
    assert full_path.name == "gittxt"
    assert (full_path / "config.py").exists()
