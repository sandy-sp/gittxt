import os
import shutil
import pytest
from gittxt.repository import RepositoryHandler

# Define test repository details
TEST_REPO_HTTPS = "https://github.com/octocat/Hello-World.git"
TEST_REPO_SSH = "git@github.com:octocat/Hello-World.git"
INVALID_REPO = "https://github.com/invalid/repository.git"
LOCAL_REPO = "/path/to/existing/local/repo"

# Updated expected directory inside `src/`
SRC_DIR = os.path.dirname(__file__)  # `tests/`
OUTPUT_DIR = os.path.join(SRC_DIR, "../src/gittxt-outputs")
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")

@pytest.fixture(scope="function")
def clean_temp_dir():
    """Ensure the temp directory is clean before each test."""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)  # Remove temp directory if it exists
    os.makedirs(TEMP_DIR, exist_ok=True)  # Recreate temp directory
    yield
    shutil.rmtree(TEMP_DIR)  # Cleanup after test

def test_clone_https_repo(clean_temp_dir):
    """Test cloning a valid HTTPS repository."""
    handler = RepositoryHandler(TEST_REPO_HTTPS)
    repo_path = handler.get_local_path()

    assert repo_path is not None, "Repository cloning failed"
    assert os.path.exists(repo_path), "Cloned repo folder does not exist"
    assert os.path.basename(repo_path) == "Hello-World", "Repository name is incorrect"

def test_clone_ssh_repo(clean_temp_dir):
    """Test cloning a valid SSH repository."""
    handler = RepositoryHandler(TEST_REPO_SSH)
    repo_path = handler.get_local_path()

    assert repo_path is not None, "Repository cloning failed"
    assert os.path.exists(repo_path), "Cloned repo folder does not exist"
    assert os.path.basename(repo_path) == "Hello-World", "Repository name is incorrect"

def test_reuse_existing_repo(clean_temp_dir):
    """Test reusing an already cloned repository."""
    handler = RepositoryHandler(TEST_REPO_HTTPS)
    repo_path1 = handler.get_local_path()
    repo_path2 = handler.get_local_path()  # Second call should not re-clone

    assert repo_path1 == repo_path2, "Repository was cloned again instead of being reused"

def test_invalid_repo(clean_temp_dir):
    """Test handling of an invalid repository URL."""
    handler = RepositoryHandler(INVALID_REPO)
    repo_path = handler.get_local_path()

    assert repo_path is None, "Invalid repository should not be cloned"

def test_local_repo():
    """Test handling of a local repository."""
    handler = RepositoryHandler(LOCAL_REPO)
    repo_path = handler.get_local_path()

    assert repo_path == LOCAL_REPO, "Local repository path was changed unexpectedly"
