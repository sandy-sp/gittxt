import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from gittxt.repository import RepositoryHandler

# Define test parameters
TEST_LOCAL_REPO = os.path.join("tests", "test-repo")
TEST_REMOTE_REPO_HTTPS = "https://github.com/sandy-sp/sandy-sp.git"
TEST_REMOTE_REPO_SSH = "git@github.com:sandy-sp/sandy-sp.git"
TEST_TEMP_DIR = os.path.join("tests", "gittxt-outputs", "temp")

@pytest.fixture(scope="function")
def clean_temp_dir():
    """Ensure the test temp directory is clean before each test."""
    if os.path.exists(TEST_TEMP_DIR):
        for file in os.listdir(TEST_TEMP_DIR):
            file_path = os.path.join(TEST_TEMP_DIR, file)
            if os.path.isdir(file_path):
                os.rmdir(file_path)
    else:
        os.makedirs(TEST_TEMP_DIR, exist_ok=True)

def test_identify_local_repo():
    """Ensure local repository paths are detected correctly."""
    repo_handler = RepositoryHandler(TEST_LOCAL_REPO)
    assert repo_handler.get_local_path() == TEST_LOCAL_REPO

@patch("git.Repo.clone_from")
def test_clone_remote_repo_https(mock_clone, clean_temp_dir):
    """Ensure HTTPS remote repositories are cloned into `gittxt-outputs/temp/`."""
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=False)
    temp_path = repo_handler.get_local_path()

    assert os.path.exists(temp_path)
    assert TEST_REMOTE_REPO_HTTPS in temp_path
    mock_clone.assert_called_once_with(TEST_REMOTE_REPO_HTTPS, temp_path, depth=1)

@patch("git.Repo.clone_from")
def test_clone_remote_repo_ssh(mock_clone, clean_temp_dir):
    """Ensure SSH remote repositories are cloned correctly."""
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_SSH, reuse_existing=False)
    temp_path = repo_handler.get_local_path()

    assert os.path.exists(temp_path)
    assert TEST_REMOTE_REPO_SSH in temp_path
    mock_clone.assert_called_once_with(TEST_REMOTE_REPO_SSH, temp_path, depth=1)

@patch("git.Repo.clone_from")
def test_reuse_existing_repo(mock_clone, clean_temp_dir):
    """Ensure an existing repository is not re-cloned if `reuse_existing_repos=True`."""
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    temp_path = repo_handler.get_local_path()

    # First time should clone
    assert os.path.exists(temp_path)
    assert mock_clone.call_count == 1

    # Second call should reuse the existing repo and not clone again
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    temp_path = repo_handler.get_local_path()

    assert mock_clone.call_count == 1  # No additional clone call

@patch("git.Repo.clone_from", side_effect=Exception("Mocked cloning error"))
def test_clone_failure(mock_clone, clean_temp_dir):
    """Ensure error handling works when cloning fails."""
    repo_handler = RepositoryHandler("https://invalid.url/repo.git", reuse_existing=False)
    temp_path = repo_handler.get_local_path()

    assert temp_path is None
    assert "Mocked cloning error" in str(mock_clone.side_effect)
