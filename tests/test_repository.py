import pytest
import os
import shutil
from unittest.mock import patch, MagicMock
from gittxt.repository import RepositoryHandler

# Define test parameters
TEST_LOCAL_REPO = os.path.abspath(os.path.join("tests", "test-repo"))
TEST_LOCAL_REPO_INVALID = os.path.abspath(os.path.join("tests", "does-not-exist"))
TEST_REMOTE_REPO_HTTPS = "https://github.com/sandy-sp/gittxt.git"
TEST_REMOTE_REPO_SSH = "git@github.com:sandy-sp/gittxt.git"

# If the updated RepositoryHandler uses the same temp directory:
TEST_TEMP_DIR = RepositoryHandler.TEMP_DIR

@pytest.fixture(scope="function")
def clean_temp_dir():
    """Ensure the test temp directory is clean before each test."""
    if os.path.exists(TEST_TEMP_DIR):
        shutil.rmtree(TEST_TEMP_DIR)
    os.makedirs(TEST_TEMP_DIR, exist_ok=True)
    # Clear the class-level clone cache to start fresh
    RepositoryHandler._clone_cache.clear()

def get_repo_name(self) -> str or None:
    """Extract repository name from the URL or local path."""
    # If it's a local directory, just return the leaf folder:
    if os.path.exists(self.source):
        return os.path.basename(os.path.normpath(self.source))

    # If it's a GitHub URL, parse to get the actual repo name
    parsed_info = parse_github_url(self.source)
    if parsed_info and parsed_info["repo"]:
        return parsed_info["repo"]

    # Fallback (old logic) if parse_github_url fails for some reason:
    parsed_url = urlparse(self.source)
    repo_name = os.path.basename(parsed_url.path).replace(".git", "").strip()
    if not repo_name:
        logger.error(f"❌ Could not extract repository name from: {self.source}")
        return None
    return repo_name

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
    get_local_path should return the same path if it's valid.
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
def test_remote_repo_https_fallback_branch(mock_clone, clean_temp_dir):
    """
    Test handling of a valid HTTPS remote repository with no explicit branch in the URL or CLI.
    Should fall back to branch='main' by default.
    """
    mock_clone.return_value = MagicMock()
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    assert local_path is not None, "Expected a non-None path for successful HTTPS clone"
    # The repo name should be 'sandy-sp'
    expected_path = os.path.join(TEST_TEMP_DIR, "gittxt")
    mock_clone.assert_called_once_with(
        TEST_REMOTE_REPO_HTTPS,
        expected_path,
        branch="main",  # fallback branch
        depth=1
    )


@patch("git.Repo.clone_from")
def test_remote_repo_ssh_fallback_branch(mock_clone, clean_temp_dir):
    """
    Test handling of a valid SSH remote repository with no explicit branch.
    Should also fall back to 'main'.
    """
    mock_clone.return_value = MagicMock()
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_SSH, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    assert local_path is not None, "Expected a non-None path for successful SSH clone"
    expected_path = os.path.join(TEST_TEMP_DIR, "gittxt")
    mock_clone.assert_called_once_with(
        TEST_REMOTE_REPO_SSH,
        expected_path,
        branch="main",
        depth=1
    )


@patch("git.Repo.clone_from")
def test_reuse_existing_clone(mock_clone, clean_temp_dir):
    """
    If reuse_existing=True and the repo was already cloned,
    the code should skip re-cloning.
    """
    RepositoryHandler._clone_cache.clear()
    # First pass: clone the repo
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    first_path = repo_handler.get_local_path()
    assert first_path is not None, "Expected a valid clone path on first clone"
    # Expect clone_from to have been called once
    assert mock_clone.call_count == 1, "Should have cloned exactly once on first call"

    # Second pass: new handler with the same source
    second_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, reuse_existing=True)
    second_path = second_handler.get_local_path()
    assert second_path == first_path, "Expected the same path if reuse_existing is True"
    # clone_from should still be called only once (cache reused)
    assert mock_clone.call_count == 1, "Should not have cloned again"


@patch("git.Repo.clone_from")
def test_clone_with_branch_override(mock_clone, clean_temp_dir):
    """
    Test that specifying a branch in the constructor
    passes the correct args to git.Repo.clone_from.
    """
    mock_clone.return_value = MagicMock()
    test_branch = "UI-Dev"
    # Clear the cache for a fresh clone
    RepositoryHandler._clone_cache.clear()
    repo_handler = RepositoryHandler(TEST_REMOTE_REPO_HTTPS, branch=test_branch, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    assert local_path is not None, "Expected successful clone with branch specified"
    expected_path = os.path.join(TEST_TEMP_DIR, "gittxt")
    mock_clone.assert_called_once_with(
        TEST_REMOTE_REPO_HTTPS,
        expected_path,
        branch=test_branch,
        depth=1
    )


@patch("git.Repo.clone_from")
def test_auto_detect_branch_from_url(mock_clone, clean_temp_dir):
    """
    If the GitHub URL includes '/tree/<branch>' but no explicit branch is provided to the constructor,
    we should auto-detect <branch> and pass it to clone_from.
    """
    mock_clone.return_value = MagicMock()
    # Example URL that includes a branch and no .git suffix
    test_url = "https://github.com/sandy-sp/gittxt/tree/UI-Dev"
    repo_handler = RepositoryHandler(test_url, reuse_existing=False)
    local_path = repo_handler.get_local_path()
    assert local_path is not None, "Expected a non-None path for a valid auto-detected branch"
    expected_path = os.path.join(TEST_TEMP_DIR, "sandy-sp")
    mock_clone.assert_called_once_with(
        test_url,
        expected_path,
        branch="dev",  # auto-detected from /tree/dev
        depth=1
    )


def test_auto_detect_sub_path():
    """
    Test that if the GitHub URL includes a subfolder (e.g. '.../tree/dev/src/utils'),
    repository.py sets 'sub_path' accordingly.
    (We don't clone here, just validate the sub_path property.)
    """
    test_url = "https://github.com/sandy-sp/ytgrid/tree/v3/ytgrid/backend/routes"
    repo_handler = RepositoryHandler(test_url, reuse_existing=False)
    # sub_path should be 'src/utils'
    assert repo_handler.sub_path == "src/utils", "Expected 'src/utils' as the sub_path from URL"
    # The branch should be 'dev'
    assert repo_handler.branch == "dev", "Expected 'dev' as the auto-detected branch"
