import pytest
from pathlib import Path
from gittxt.core.repository import RepositoryHandler
import uuid

TEST_REPO = Path("tests/test_repo")

@pytest.mark.asyncio
async def test_local_repo_path_resolution():
    handler = RepositoryHandler(TEST_REPO)
    path = await handler.resolve()
    assert path.exists(), "Resolved local path does not exist"
    assert (path / "README.md").exists(), "README.md not found in local repo"

@pytest.mark.asyncio
async def test_invalid_repo_path_resolution():
    fake_path = Path(f"nonexistent_{uuid.uuid4().hex}")
    handler = RepositoryHandler(fake_path)
    resolved_path = await handler.resolve()
    assert not resolved_path.exists(), "Expected resolved path to not exist for invalid repo"

@pytest.mark.asyncio
async def test_invalid_github_repo_clone():
    handler = RepositoryHandler("https://github.com/invalid/repo", branch="main")
    with pytest.raises(RuntimeError):
        await handler.resolve()

@pytest.mark.asyncio
async def test_subdir_scan_resolution(tmp_path):
    handler = RepositoryHandler(
        "https://github.com/sandy-sp/gittxt",
        branch="main",
        subdir="src/gittxt",
        cache_dir=tmp_path
    )

    # Ensure repo is cloned and handler state is initialized
    await handler.resolve()

    # Now fetch subdir path
    repo_path, subdir, _, _, _ = handler.get_local_path()
    scan_root = Path(repo_path) / subdir if subdir else Path(repo_path)

    assert scan_root.exists()
    assert (scan_root / "cli").exists(), "Expected cli/ folder to exist in resolved subdir"
