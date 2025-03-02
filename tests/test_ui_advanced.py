import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from src.gittxt_ui.app import app
from src.gittxt_ui.routes import UPLOADS_DIR, OUTPUT_FORMAT_DIRS

client = TestClient(app)

def test_ui_scan_and_file_generation():
    """Ensure UI initiates a scan and generates expected output."""
    response = client.post("/scan/", data={"repo_path": ".", "output_format": "txt"})
    assert response.status_code == 200
    assert response.json()["message"] == "Scan started"

    # Verify the generated output file
    test_file_path = Path(UPLOADS_DIR) / "text" / "test-output.txt"
    assert test_file_path.exists(), "Expected file missing after UI scan!"

def test_ui_file_serving():
    """Ensure UI can correctly serve files after scan."""
    # Ensure a dummy file exists
    test_file_path = Path(UPLOADS_DIR) / "text" / "test-output.txt"
    test_file_path.parent.mkdir(parents=True, exist_ok=True)
    test_file_path.write_text("Test content for UI serving.")

    response = client.get("/download/txt/test-output.txt")
    assert response.status_code == 200, "File download failed!"
    assert "content-disposition" in response.headers, "Missing content disposition header!"
