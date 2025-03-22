import pytest
from fastapi.testclient import TestClient
from click.testing import CliRunner
from gittxt_api.app import app
from gittxt.cli import cli
from pathlib import Path


@pytest.fixture(scope="session")
def cli_runner():
    """CLI runner fixture for Click-based CLI tests"""
    return CliRunner()


@pytest.fixture(scope="session")
def api_client():
    """FastAPI test client for API tests"""
    return TestClient(app)


@pytest.fixture(scope="session")
def test_repo(tmp_path_factory):
    """
    Creates a mock repo structure for CLI, API, and unit tests.
    Mimics a small repo with a variety of file types.
    """
    repo_dir = tmp_path_factory.mktemp("test-repo")

    # Create folders
    (repo_dir / "src").mkdir()
    (repo_dir / "docs").mkdir()
    (repo_dir / "data").mkdir()
    (repo_dir / "assets").mkdir()

    # Create files
    (repo_dir / "src" / "example.py").write_text("print('Hello world')\n")
    (repo_dir / "docs" / "README.md").write_text("# Sample Documentation\n")
    (repo_dir / "data" / "sample.csv").write_text("id,value\n1,100\n")
    (repo_dir / "assets" / "image.png").write_bytes(b"PNGDATA")
    (repo_dir / ".gitignore").write_text("*.png\n")

    return repo_dir


@pytest.fixture
def empty_repo(tmp_path):
    """
    Creates an empty repo (no files) for edge case tests.
    """
    empty = tmp_path / "empty-repo"
    empty.mkdir()
    return empty
