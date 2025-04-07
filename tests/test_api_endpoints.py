import os
import shutil
import zipfile
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from gittxt.api.main import app

client = TestClient(app)

TEST_REPO_PATH = Path("tests/test_repo")
TEST_ZIP_PATH = Path("tests/test_repo.zip")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR = Path("uploads")


@pytest.fixture(scope="session", autouse=True)
def setup_test_repo():
    # Create a small repo structure
    TEST_REPO_PATH.mkdir(parents=True, exist_ok=True)
    (TEST_REPO_PATH / "main.py").write_text("print('Hello world')\n")
    (TEST_REPO_PATH / "README.md").write_text("# Test Repo\nThis is a test.")

    # Create ZIP
    with zipfile.ZipFile(TEST_ZIP_PATH, 'w') as zipf:
        for file_path in TEST_REPO_PATH.rglob("*"):
            arcname = file_path.relative_to(TEST_REPO_PATH.parent)
            zipf.write(file_path, arcname)

    yield

    # Cleanup
    shutil.rmtree(TEST_REPO_PATH.parent / "outputs", ignore_errors=True)
    shutil.rmtree(TEST_REPO_PATH.parent / "uploads", ignore_errors=True)
    shutil.rmtree(TEST_REPO_PATH, ignore_errors=True)
    TEST_ZIP_PATH.unlink(missing_ok=True)


@pytest.fixture(scope="module")
def scan_id():
    """Create a scan and return its ID for other tests to use"""
    response = client.post("/scan", json={"repo_path": str(TEST_REPO_PATH), "lite": True})
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    return data["scan_id"]


def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_inspect_endpoint():
    response = client.post("/inspect", json={"repo_path": str(TEST_REPO_PATH)})
    assert response.status_code == 200
    data = response.json()
    assert "repo_name" in data
    assert "tree" in data
    assert data["file_count"] == 2


def test_scan_endpoint(scan_id):
    # We already created the scan in the fixture, just verify the response format
    response = client.post("/scan", json={"repo_path": str(TEST_REPO_PATH), "lite": True})
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["repo_name"] == TEST_REPO_PATH.name


def test_summary_endpoint(scan_id):
    response = client.get(f"/summary/{scan_id}")
    assert response.status_code == 200
    assert "summary" in response.json()


@pytest.mark.parametrize("format", ["txt", "md", "json", "zip"])
def test_download_formats(scan_id, format):
    response = client.get(f"/download/{scan_id}?format={format}")
    assert response.status_code == 200
    assert "attachment" in response.headers.get("content-disposition", "")


def test_download_artifacts_zip(scan_id):
    response = client.get(f"/download/{scan_id}/artifacts")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"


def test_upload_endpoint():
    with open(TEST_ZIP_PATH, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("test_repo.zip", f, "application/zip")},
            data={"lite": "true"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert "repo_name" in data
    assert "textual_files" in data
    assert "tree" in data


def test_cleanup_endpoint(scan_id):
    response = client.delete(f"/cleanup/{scan_id}")
    assert response.status_code == 200
    assert "cleaned up" in response.json()["detail"]


# Add test for error handling
def test_invalid_scan_id():
    response = client.get("/summary/nonexistent-id")
    assert response.status_code == 404


def test_invalid_repo_path():
    response = client.post("/scan", json={"repo_path": "/nonexistent/path"})
    assert response.status_code in (400, 404, 422)
