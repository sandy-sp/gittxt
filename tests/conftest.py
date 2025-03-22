import pytest
from fastapi.testclient import TestClient
from click.testing import CliRunner
from gittxt.cli import cli
from pathlib import Path
from gittxt_api.app import app

@pytest.fixture(scope="session")
def cli_runner():
    return CliRunner()


@pytest.fixture(scope="session")
def api_client():
    return TestClient(app)


@pytest.fixture(scope="session")
def test_repo(tmp_path_factory):
    # Create test-repo folder structure
    repo_dir = tmp_path_factory.mktemp("test-repo")

    (repo_dir / "src").mkdir()
    (repo_dir / "docs").mkdir()
    (repo_dir / "data").mkdir()

    (repo_dir / "src" / "example.py").write_text("print('Hello world')\n")
    (repo_dir / "docs" / "README.md").write_text("# Sample Documentation\n")
    (repo_dir / "data" / "sample.csv").write_text("id,value\n1,100\n")
    (repo_dir / "image.png").write_bytes(b"PNGDATA")
    (repo_dir / ".gitignore").write_text("*.png\n")

    return repo_dir
