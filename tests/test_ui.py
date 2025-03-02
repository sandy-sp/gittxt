import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from src.gittxt_ui.app import app
from src.gittxt_ui.routes import UPLOADS_DIR, OUTPUT_FORMAT_DIRS

client = TestClient(app)

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

def test_download_api():
    """Ensure file download API works correctly for all formats."""
    for output_format in ["txt", "json", "md"]:
        # Ensure test file exists
        test_file_path = Path(UPLOADS_DIR) / OUTPUT_FORMAT_DIRS[output_format] / f"test-output.{output_format}"
        test_file_path.parent.mkdir(parents=True, exist_ok=True)
        test_file_path.write_text("Test file content")  # Create dummy file

        response = client.get(f"/download/{output_format}/test-output.{output_format}")
        assert response.status_code == 200, f"Failed to download {output_format} file."
        assert "content-disposition" in response.headers
