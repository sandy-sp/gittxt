import pytest
from pathlib import Path
from gittxt.core.repository import RepositoryHandler

TEST_REPO = Path("tests/test_repo")


def test_local_repo_path_resolution():
    handler = RepositoryHandler(source="local", path=TEST_REPO)
    path = handler.get_local_path()
    assert path.exists(), "Resolved local path does not exist"
    assert (path / "README.md").exists(), "Expected README.md not found in local repo"


def test_invalid_repo_path_raises():
    handler = RepositoryHandler(source="local", path=Path("non_existent_folder"))
    with pytest.raises(FileNotFoundError):
        handler.get_local_path()


@pytest.mark.asyncio
async def test_invalid_github_repo_clone():
    handler = RepositoryHandler(
        source="github",
        url="https://github.com/invalid/repo",
        branch="main"
    )
    with pytest.raises(RuntimeError):
        await handler.get_local_path()


@pytest.mark.asyncio
async def test_subdir_scan_resolution(tmp_path):
    handler = RepositoryHandler(
        source="github",
        url="https://github.com/sandy-sp/gittxt",
        branch="main",
        subdir="src/gittxt",
        cache_dir=tmp_path
    )
    path = await handler.get_local_path()
    assert path.exists(), "Resolved subdir path does not exist"
    assert path.name == "gittxt", "Subdir name mismatch"
