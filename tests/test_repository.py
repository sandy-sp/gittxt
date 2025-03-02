import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from gittxt.repository import RepositoryHandler

# Define test parameters:
TEST_LOCAL_REPO = os.path.abspath(os.path.join("tests", "test-repo"))
TEST_LOCAL_REPO_INVALID = os.path.abspath(os.path.join("tests", "does-not-exist"))
TEST_REMOTE_REPO_HTTPS = "https://github.com/sandy-sp/sandy-sp.git"
TEST_REMOTE_REPO_SSH = "git@github.com:sandy-sp/sandy-sp.git"

# Use the production TEMP_DIR from RepositoryHandler
TEST_TEMP_DIR = RepositoryHandler.TEMP_DIR

@pytest.fixture(scope="function")
def clean_temp_dir():
    """Ensure the test temp directory is clean before each test."""
    if os.path.exists(TEST_TEMP_DIR):
        shutil.rmtree(TEST_TEMP_DIR)
    os.makedirs(TEST_TEMP_DIR, exist_ok=True)
    # Clear the class-level clone cache before each test
    RepositoryHandler._clone_cache.clear()

@patch("git.Repo.clone_from", side_effect=Exception("Mocked cloning error"))
def test_clone_failure(mock_clone, clean_temp_dir):
    """
    Ensure error handling works when cloning fails.
    The function should return None if an exception occurs.
    """
    repo_handler = RepositoryHandler("https://invalid.url/repo.git", reuse_existing=False)
    temp_path = repo_handler.get_local_path()
    assert temp_path is None, "Expected None when cloning fails"
    mock_clone.assert_called_once()

def test_local_repo_valid(clean_temp_dir):
    """
    Ensure valid local repositories are correctly returned without modification.
    """
    os.makedirs(TEST_LOCAL_REPO, exist_ok=True)
    repo_handler = RepositoryHandler(TEST_LOCAL_REPO, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    assert local_path == TEST_LOCAL_REPO, "Expected local path to be returned unchanged."

def test_local_repo_invalid(clean_temp_dir):
    """
    Ensure an invalid local path results in None.
    """
    repo_handler = RepositoryHandler(TEST_LOCAL_REPO_INVALID, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    assert local_path is None, "Expected None for an invalid local path."

@patch("git.Repo.clone_from")
def test_remote_repo_https(mock_clone, clean_temp_dir):
    """
    Test cloning from a valid HTTPS remote repository.
    """
    mock_clone.return_value = MagicMock()
    
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=False)
    local_path = repo_handler.get_local_path()

    assert local_path is not None, "Expected non-None path for HTTPS clone."

    expected_path = os.path.join(TEST_TEMP_DIR, "sandy-sp")
    mock_clone.assert_called_once()
    
    args, kwargs = mock_clone.call_args
    assert args == (TEST_REMOTE_REPO_HTTPS, expected_path), "Unexpected repo clone path"
    assert kwargs.get("depth") == 1, "Depth argument missing"

@patch("git.Repo.clone_from")
def test_remote_repo_ssh(mock_clone, clean_temp_dir):
    """
    Test cloning from a valid SSH remote repository.
    """
    mock_clone.return_value = MagicMock()

    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_SSH, reuse_existing=False)
    local_path = repo_handler.get_local_path()

    assert local_path is not None, "Expected non-None path for SSH clone."
    mock_clone.assert_called_once()

@patch("git.Repo.clone_from")
def test_reuse_existing_clone(mock_clone, clean_temp_dir):
    """
    Ensure reusing an existing clone prevents redundant cloning.
    """
    RepositoryHandler._clone_cache.clear()

    # First clone
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    first_path = repo_handler.get_local_path()

    assert first_path is not None, "Expected a valid clone path on first execution."
    assert mock_clone.call_count == 1, "Should have cloned exactly once."

    # Second call should not trigger another clone
    second_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    second_path = second_handler.get_local_path()

    assert second_path == first_path, "Expected identical paths on reuse."
    assert mock_clone.call_count == 1, "Should not have cloned again."

@patch("git.Repo.clone_from")
def test_clone_with_branch(mock_clone, clean_temp_dir):
    """
    Ensure the branch parameter is correctly passed when cloning.
    """
    mock_clone.return_value = MagicMock()
    test_branch = "my-feature-branch"

    RepositoryHandler._clone_cache.clear()

    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, branch=test_branch, reuse_existing=False)
    local_path = repo_handler.get_local_path()

    assert local_path is not None, "Expected successful clone with specified branch."

    expected_path = os.path.join(TEST_TEMP_DIR, "sandy-sp")
    mock_clone.assert_called_once_with(
        TEST_REMOTE_REPO_HTTPS,
        expected_path,
        branch=test_branch,
        depth=1
    )
