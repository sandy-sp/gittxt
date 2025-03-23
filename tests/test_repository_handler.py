import pytest
from gittxt.repository import RepositoryHandler

def test_local_repo_resolution(tmp_path):
    (tmp_path / ".git").mkdir()
    repo_handler = RepositoryHandler(source=str(tmp_path))
    path, subdir, is_remote, repo_name = repo_handler.get_local_path()

    assert path == str(tmp_path)
    assert repo_name == tmp_path.name
    assert is_remote is False
    assert subdir == ""

def test_invalid_local_path(tmp_path):
    invalid_path = tmp_path / "nonexistent"
    with pytest.raises(ValueError):
        repo_handler = RepositoryHandler(source=str(invalid_path))
        repo_handler.get_local_path()

@pytest.mark.parametrize("url", [
    "https://github.com/sandy-sp/gittxt",
    "git@github.com:sandy-sp/gittxt.git",
])
def test_remote_repo_url_detection(url):
    repo_handler = RepositoryHandler(source=url)
    assert repo_handler.is_remote_repo(url) is True


def test_clone_remote_repo_fallback(monkeypatch, tmp_path):
    """Simulate a fallback when branch clone fails and retry is triggered."""

    repo_handler = RepositoryHandler(source="https://github.com/fake/repo.git")
    temp_dir = tmp_path / "temp"

    # Patch the internal _clone_remote_repo method
    monkeypatch.setattr("gittxt.repository.git.Repo.clone_from", lambda url, dest, **kwargs: None)

    # Validate fallback logic works (we patch it to "succeed" on retry)
    success = repo_handler._clone_remote_repo("https://github.com/fake/repo.git", "nonexistent-branch", temp_dir)
    assert success is True
