import pytest
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from gittxt.repository import RepositoryHandler

# Define test parameters
TEST_LOCAL_REPO = Path("tests/test-repo").resolve()
TEST_LOCAL_REPO_INVALID = Path("tests/does-not-exist").resolve()
TEST_REMOTE_REPO_HTTPS = "https://github.com/sandy-sp/gittxt.git"
TEST_REMOTE_REPO_SSH = "git@github.com:sandy-sp/gittxt.git"
TEST_TEMP_DIR = RepositoryHandler.TEMP_DIR

@pytest.fixture(scope="function")
def clean_temp_dir():
    if TEST_TEMP_DIR.exists():
        shutil.rmtree(TEST_TEMP_DIR)
    TEST_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    RepositoryHandler._clone_cache.clear()

@patch("git.Repo.clone_from", side_effect=Exception("Mocked cloning error"))
def test_clone_failure(mock_clone, clean_temp_dir):
    repo_handler = RepositoryHandler("https://invalid.url/repo.git", reuse_existing=False)
    temp_path = repo_handler.get_local_path()
    assert temp_path is None
    mock_clone.assert_called_once()

def test_local_repo_valid(clean_temp_dir):
    TEST_LOCAL_REPO.mkdir(parents=True, exist_ok=True)
    repo_handler = RepositoryHandler(TEST_LOCAL_REPO, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    assert local_path == str(TEST_LOCAL_REPO)

def test_local_repo_invalid(clean_temp_dir):
    repo_handler = RepositoryHandler(TEST_LOCAL_REPO_INVALID, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    assert local_path is None

@patch("git.Repo.clone_from")
def test_remote_repo_https(mock_clone, clean_temp_dir):
    mock_clone.return_value = MagicMock()
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    expected_dir = TEST_TEMP_DIR / "sandy-sp"
    assert local_path is not None
    mock_clone.assert_called_once_with(TEST_REMOTE_REPO_HTTPS, str(expected_dir), depth=1)

@patch("git.Repo.clone_from")
def test_remote_repo_ssh(mock_clone, clean_temp_dir):
    mock_clone.return_value = MagicMock()
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_SSH, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    assert local_path is not None
    mock_clone.assert_called_once()

@patch("git.Repo.clone_from")
def test_reuse_existing_clone(mock_clone, clean_temp_dir):
    RepositoryHandler._clone_cache.clear()
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    first_path = repo_handler.get_local_path()
    assert first_path is not None
    assert mock_clone.call_count == 1

    second_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    second_path = second_handler.get_local_path()
    assert second_path == first_path
    assert mock_clone.call_count == 1

@patch("git.Repo.clone_from")
def test_clone_with_branch(mock_clone, clean_temp_dir):
    mock_clone.return_value = MagicMock()
    test_branch = "UI-Dev"
    RepositoryHandler._clone_cache.clear()
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, branch=test_branch, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    expected_dir = TEST_TEMP_DIR / "gittxt"
    assert local_path is not None
    mock_clone.assert_called_once_with(
        TEST_REMOTE_REPO_HTTPS,
        str(expected_dir),
        branch=test_branch,
        depth=1
    )