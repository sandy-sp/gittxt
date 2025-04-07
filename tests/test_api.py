import os
import shutil
import pytest
from fastapi.testclient import TestClient
from uuid import UUID

# Import your FastAPI app
from gittxt.api.main import app

client = TestClient(app)

# Example local/remote test repos
TEST_LOCAL_REPO = "tests/test_repo"
TEST_REMOTE_REPO = "https://github.com/octocat/Hello-World"

@pytest.fixture
def ensure_test_repo():
    """Optional fixture if you have a local test repo."""
    yield
    # teardown if needed

def test_health():
    """
    Basic test to ensure the API is running.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

@pytest.mark.usefixtures("ensure_test_repo")
def test_inspect_local():
    """
    Test the /inspect endpoint on a local test repo.
    """
    response = client.post(
        "/inspect",
        params={"repo_path": TEST_LOCAL_REPO},
    )
    assert response.status_code == 200, response.text
    data = response.json()

    # We expect the new structure under "repository", "files", etc.
    assert "repository" in data, "Expected 'repository' key in response"
    assert "files" in data, "Expected 'files' key in response"
    assert "assets" in data, "Expected 'assets' key in response"
    assert "summary" in data, "Expected 'summary' key in response"

    # Check that repository has a 'name'
    assert "name" in data["repository"]
    # Check that summary has some basics
    # (exact fields depend on your code – adapt as needed)
    assert "total_files" in data["summary"] or "estimated_tokens" in data["summary"]
    # Confirm we got a list of files
    assert isinstance(data["files"], list)

@pytest.mark.usefixtures("ensure_test_repo")
def test_inspect_remote():
    """
    Test the /inspect endpoint on a small public GitHub repo (if desired).
    """
    response = client.post(
        "/inspect",
        params={
            "repo_path": TEST_REMOTE_REPO,
            "branch": "master"  # or "main" depending on the remote
        },
    )
    if response.status_code == 500:
        pytest.skip("Remote repo might be unavailable or not recognized.")
    else:
        assert response.status_code == 200, response.text
        data = response.json()

        assert "repository" in data, "Expected 'repository' key in response"
        assert "files" in data, "Expected 'files' key in response"
        assert isinstance(data["files"], list), "files should be a list"

        # If your code returns "assets" even for remote
        # or might be an empty list, just confirm it's there
        assert "assets" in data
        assert "summary" in data

def test_scan_local():
    """
    Scan the local test repo with /scan, expecting subfolders and a scan_id.
    """
    response = client.post(
        "/scan",
        params={
            "repo_path": TEST_LOCAL_REPO,
            "lite": "false"
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()

    # Check for a valid scan_id
    scan_id = data["scan_id"]
    assert isinstance(scan_id, str)
    UUID(scan_id)  # raises ValueError if invalid

    # Basic checks
    assert data["num_textual_files"] >= 0

    # We'll store the scan_id for use in subsequent tests
    return scan_id

def test_scan_remote():
    """
    Optionally test the /scan on a remote repo. 
    Might skip if no network or the repo is large.
    """
    response = client.post(
        "/scan",
        params={
            "repo_path": TEST_REMOTE_REPO,
            "branch": "main",
            "lite": "true"
        },
    )
    if response.status_code == 500:
        pytest.skip("Remote repo might be unavailable or not recognized.")
    else:
        data = response.json()
        scan_id = data["scan_id"]
        UUID(scan_id)

def test_scan_and_followup():
    """
    Demonstrate a scenario:
    1) /scan
    2) /summary
    3) /download
    4) /cleanup
    """
    # 1) /scan local
    scan_resp = client.post("/scan", params={"repo_path": TEST_LOCAL_REPO})
    assert scan_resp.status_code == 200
    scan_data = scan_resp.json()
    scan_id = scan_data["scan_id"]

    # 2) /summary
    summary_resp = client.get(f"/summary/{scan_id}")
    assert summary_resp.status_code == 200, summary_resp.text
    summary_data = summary_resp.json()
    # E.g. confirm "repository" or something else is in the summary
    assert "repository" in summary_data or len(summary_data) > 0

    # 3) /download .json
    download_resp = client.get(f"/download/{scan_id}", params={"format": "json"})
    assert download_resp.status_code == 200, download_resp.text
    content_disp = download_resp.headers.get("content-disposition", "")
    assert "attachment" in content_disp or "filename" in content_disp

    # 4) /cleanup
    cleanup_resp = client.delete(f"/cleanup/{scan_id}")
    assert cleanup_resp.status_code == 200, cleanup_resp.text
    cleanup_data = cleanup_resp.json()
    assert cleanup_data["status"] == "ok"

    # Ensure subsequent summary is 404 now
    summary_resp2 = client.get(f"/summary/{scan_id}")
    assert summary_resp2.status_code == 404

def test_upload_zip():
    """
    Test the /upload endpoint by zipping a small test folder.
    We'll create a small .zip in memory (or from disk), then pass it to /upload.
    """
    import zipfile
    import tempfile
    import pathlib

    tmp_dir = tempfile.mkdtemp(prefix="gittxt_test_")
    zip_path = os.path.join(tmp_dir, "test_upload.zip")

    # Zip up the local repo
    with zipfile.ZipFile(zip_path, "w") as zf:
        repo_path = pathlib.Path(TEST_LOCAL_REPO)
        for p in repo_path.rglob("*"):
            if p.is_file():
                zf.write(p, arcname=p.relative_to(repo_path))

    with open(zip_path, "rb") as f:
        files = {"file": ("test_upload.zip", f, "application/zip")}
        resp = client.post("/upload", files=files)
    shutil.rmtree(tmp_dir, ignore_errors=True)

    assert resp.status_code == 200, resp.text
    data = resp.json()
    scan_id = data["scan_id"]
    assert isinstance(scan_id, str)
    # We can further test /download or /summary if needed
