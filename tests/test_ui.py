import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import time
from gittxt_ui.app import app
from gittxt_ui.routes import UPLOADS_DIR, OUTPUT_FORMAT_DIRS

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_test_environment(tmp_path):
    """Setup temporary test directories and files for UI API tests."""
    test_dir = tmp_path / "uploads"
    test_dir.mkdir()

    # Create subdirectories for different formats
    for fmt in OUTPUT_FORMAT_DIRS.values():
        (test_dir / fmt).mkdir(parents=True, exist_ok=True)

    return test_dir

def test_homepage():
    """Ensure the homepage loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Gittxt Web Interface" in response.text

def test_scan_api():
    """Ensure the /scan/ API triggers correctly and completes."""
    response = client.post("/scan/", json={"repo_path": "test_repo", "output_format": "txt"})  # ✅ Use JSON instead of form data
    assert response.status_code == 200
    assert response.json()["message"] == "Scan started"
    
    pid = response.json().get("pid")
    assert pid is not None, "Scan did not return a valid process ID."
    
    time.sleep(3)  # Allow time for scanning
    
    status_response = client.get(f"/scan/status/{pid}")
    assert status_response.status_code == 200
    assert status_response.json()["status"] in ["running", "completed"], "Scan did not start properly!"

def test_websocket_scan_progress():
    """Ensure WebSocket updates are received for scan progress."""
    with client.websocket_connect("/ws/progress/") as websocket:
        progress_updates = []
        for _ in range(10):
            try:
                data = websocket.receive_text(timeout=5)  # ✅ Increased timeout to handle delays
                progress_updates.append(data)
            except Exception:
                break  # Stop receiving if no data comes
        
        assert len(progress_updates) > 0, "No progress updates received!"  # ✅ Ensure at least 1 update
        assert any("Processing file" in update for update in progress_updates), "Expected progress messages!"
        assert any("✅ Scan completed successfully!" in progress_updates), "Completion message missing!"


@pytest.mark.parametrize("output_format", ["txt", "json", "md"])
def test_download_api(output_format, setup_test_environment):
    """Ensure file download API works correctly for different formats."""
    repo_output_dir = Path(UPLOADS_DIR) / "results" / "test_repo" / OUTPUT_FORMAT_DIRS[output_format]
    test_file_path = repo_output_dir / f"test-output.{output_format}"

    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    test_file_path.write_text("Test file content")

    response = client.get(f"/download/test_repo/all")
    assert response.status_code == 200, f"Failed to download {output_format} file."
    assert "content-disposition" in response.headers
    assert response.headers["content-type"] in ["application/octet-stream", "application/zip"], "Unexpected file type!"


def test_invalid_download():
    """Ensure requesting a non-existent file returns 404."""
    response = client.get("/download/txt/nonexistent.txt")
    assert response.status_code == 404
    assert response.json()["detail"] in ["File not found.", "Not Found"], "Unexpected error message!"

