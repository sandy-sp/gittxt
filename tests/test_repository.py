import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from gittxt.repository import RepositoryHandler

# Define test parameters
TEST_LOCAL_REPO = os.path.abspath(os.path.join("tests", "test-repo"))
TEST_REMOTE_REPO_HTTPS = "https://github.com/sandy-sp/sandy-sp.git"
TEST_REMOTE_REPO_SSH = "git@github.com:sandy-sp/sandy-sp.git"
TEST_TEMP_DIR = os.path.abspath(os.path.join("tests", "gittxt-outputs", "temp"))

@pytest.fixture(scope="function")
def clean_temp_dir():
    """Ensure the test temp directory is clean before each test."""
    if os.path.exists(TEST_TEMP_DIR):
        shutil.rmtree(TEST_TEMP_DIR)  # Ensure a fresh directory
    os.makedirs(TEST_TEMP_DIR, exist_ok=True)

@patch("git.Repo.clone_from", side_effect=Exception("Mocked cloning error"))
def test_clone_failure(mock_clone, clean_temp_dir):
    """Ensure error handling works when cloning fails."""
    repo_handler = RepositoryHandler("https://invalid.url/repo.git", reuse_existing=False)
    temp_path = repo_handler.get_local_path()

    assert temp_path is None  # The function should return None, not raise an error
    mock_clone.assert_called_once()  # Ensure cloning was attempted
