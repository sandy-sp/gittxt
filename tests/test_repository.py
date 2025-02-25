import pytest
from gittxt.repository import RepositoryHandler

def test_is_remote_repo():
    """Test detection of remote repositories."""
    remote_repo = RepositoryHandler("https://github.com/sandy-sp/gittxt.git")
    assert remote_repo.is_remote_repo() is True

    local_repo = RepositoryHandler("/home/user/project")
    assert local_repo.is_remote_repo() is False
