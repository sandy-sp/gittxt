import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import time
from src.gittxt_ui.app import app
from src.gittxt_ui.routes import UPLOADS_DIR, OUTPUT_FORMAT_DIRS

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
    """Ensure the /scan/ API triggers correctly."""
    response = client.post("/scan/", data={"repo_path": ".", "output_format": "txt"})
    assert response.status_code == 200
    assert response.json()["message"] == "Scan started"


def test_websocket_scan_progress():
    """Ensure WebSocket updates are received for scan progress."""
    with client.websocket_connect("/ws/progress/") as websocket:
        # Expect progress updates (simulated in backend)
        progress_updates = []
        for _ in range(10):  # Expecting 10 progress updates
            data = websocket.receive_text()
            progress_updates.append(data)
            time.sleep(0.5)  # Simulate network delay

        assert any("Processing file" in update for update in progress_updates), "Expected progress messages!"
        assert "✅ Scan completed successfully!" in progress_updates, "Expected scan completion message!"


@pytest.mark.parametrize("output_format", ["txt", "json", "md"])
def test_download_api(output_format, setup_test_environment):
    """Ensure file download API works correctly for different formats."""
    
    test_file_path = setup_test_environment / OUTPUT_FORMAT_DIRS[output_format] / f"test-output.{output_format}"
    
    # ✅ Ensure file exists before testing
    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    test_file_path.write_text("Test file content")

    response = client.get(f"/download/{output_format}/test-output.{output_format}")

    assert response.status_code == 200, f"Failed to download {output_format} file."
    assert "content-disposition" in response.headers
    assert response.headers["content-type"] == "application/octet-stream"

def test_invalid_download():
    """Ensure requesting a non-existent file returns 404."""
    response = client.get("/download/txt/nonexistent.txt")
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found."
