import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import time
from gittxt_ui.app import app
from gittxt_ui.routes import UPLOADS_DIR, OUTPUT_FORMAT_DIRS

client = TestClient(app)

def test_ui_scan_and_file_generation():
    """Ensure UI initiates a scan and generates expected output."""
    response = client.post("/scan/", json={"repo_path": "test_repo", "output_format": "txt"})
    assert response.status_code == 200
    assert response.json()["message"] == "Scan started"

    pid = response.json().get("pid")
    assert pid is not None, "Scan did not return a valid process ID."

    time.sleep(3)  # Allow time for scanning

    # Check if scan completed
    status_response = client.get(f"/scan/status/{pid}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] in ["running", "completed"], "Scan did not start properly!"

    # ✅ Retry file existence check for slow file creation
    repo_output_dir = Path(UPLOADS_DIR) / "results" / "test_repo" / "text"
    test_file_path = repo_output_dir / "test_repo.txt"

    max_attempts = 10
    for _ in range(max_attempts):
        if test_file_path.exists():
            break
        time.sleep(1)  # ✅ Wait and retry

    assert test_file_path.exists(), f"Expected output file missing: {test_file_path}"


def test_ui_file_serving():
    """Ensure UI can correctly serve files after scan."""
    repo_output_dir = Path(UPLOADS_DIR) / "results" / "test_repo" / "text"
    test_file_path = repo_output_dir / "test-output.txt"
    
    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    test_file_path.write_text("Test content for UI serving.")
    
    response = client.get("/download/test_repo/all")
    assert response.status_code == 200, "File download failed!"
    assert "content-disposition" in response.headers, "Missing content disposition header!"
    assert response.headers["content-type"] == "application/zip", "Incorrect file type for download."
