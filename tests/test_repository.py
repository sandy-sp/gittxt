import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from gittxt.repository import RepositoryHandler

# Define test parameters
TEST_LOCAL_REPO = os.path.abspath(os.path.join("tests", "test-repo"))
TEST_LOCAL_REPO_INVALID = os.path.abspath(os.path.join("tests", "does-not-exist"))
TEST_REMOTE_REPO_HTTPS = "https://github.com/sandy-sp/sandy-sp.git"
TEST_REMOTE_REPO_SSH = "git@github.com:sandy-sp/sandy-sp.git"
TEST_TEMP_DIR = os.path.abspath(os.path.join("tests", "gittxt-outputs", "temp"))

@pytest.fixture(scope="function")
def clean_temp_dir():
    """Ensure the test temp directory is clean before each test."""
    if os.path.exists(TEST_TEMP_DIR):
        shutil.rmtree(TEST_TEMP_DIR)
    os.makedirs(TEST_TEMP_DIR, exist_ok=True)

@patch("git.Repo.clone_from", side_effect=Exception("Mocked cloning error"))
def test_clone_failure(mock_clone, clean_temp_dir):
    """
    Ensure error handling works when cloning fails.
    We expect None to be returned if the clone attempt raises an exception.
    """
    repo_handler = RepositoryHandler("https://invalid.url/repo.git", reuse_existing=False)
    temp_path = repo_handler.get_local_path()

    assert temp_path is None, "Expected None when cloning fails"
    mock_clone.assert_called_once()

def test_local_repo_valid(clean_temp_dir):
    """
    Ensure we can handle an existing local repository path correctly.
    This test checks that get_local_path returns the same path if it's valid.
    """
    os.makedirs(TEST_LOCAL_REPO, exist_ok=True)

    repo_handler = RepositoryHandler(TEST_LOCAL_REPO, reuse_existing=False)
    local_path = repo_handler.get_local_path()

    assert local_path == TEST_LOCAL_REPO, "Expected the local path for a valid local repo"

def test_local_repo_invalid(clean_temp_dir):
    """
    Ensure we return None for an invalid local path.
    """
    repo_handler = RepositoryHandler(TEST_LOCAL_REPO_INVALID, reuse_existing=False)
    local_path = repo_handler.get_local_path()

    assert local_path is None, "Expected None for an invalid local path"

@patch("git.Repo.clone_from")
def test_remote_repo_https(mock_clone, clean_temp_dir):
    """
    Test handling of a valid HTTPS remote repository.
    """
    mock_clone.return_value = MagicMock()

    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=False)
    local_path = repo_handler.get_local_path()

    assert local_path is not None, "Expected a non-None path for successful HTTPS clone"
    # The repo name is 'sandy-sp' if we parse that from the URL
    expected_path = os.path.join(TEST_TEMP_DIR, "sandy-sp")
    mock_clone.assert_called_once_with(TEST_REMOTE_REPO_HTTPS, expected_path, depth=1)

@patch("git.Repo.clone_from")
def test_remote_repo_ssh(mock_clone, clean_temp_dir):
    """
    Test handling of a valid SSH remote repository.
    """
    mock_clone.return_value = MagicMock()

    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_SSH, reuse_existing=False)
    local_path = repo_handler.get_local_path()

    assert local_path is not None, "Expected a non-None path for successful SSH clone"
    mock_clone.assert_called_once()

@patch("git.Repo.clone_from")
def test_reuse_existing_clone(mock_clone, clean_temp_dir):
    """
    If reuse_existing=True and the repo was already cloned,
    the code should skip re-cloning.
    """
    # 1. First pass: clone the repo
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    first_path = repo_handler.get_local_path()
    assert first_path is not None
    assert mock_clone.call_count == 1, "Should have cloned exactly once"

    # 2. Second pass: same repo, new handler
    second_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    second_path = second_handler.get_local_path()

    assert second_path == first_path, "Expected the same path if reuse_existing is True"
    assert mock_clone.call_count == 1, "Should not have cloned again"

@patch("git.Repo.clone_from")
def test_clone_with_branch(mock_clone, clean_temp_dir):
    """
    Test that specifying a branch passes the correct args to git.Repo.clone_from.
    """
    mock_clone.return_value = MagicMock()
    test_branch = "my-feature-branch"

    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, branch=test_branch, reuse_existing=False)
    local_path = repo_handler.get_local_path()

    assert local_path is not None, "Expected successful clone"
    expected_path = os.path.join(TEST_TEMP_DIR, "sandy-sp")
    mock_clone.assert_called_once_with(
        TEST_REMOTE_REPO_HTTPS,
        expected_path,
        branch=test_branch,
        depth=1
    )
