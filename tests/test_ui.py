import pytest
from fastapi.testclient import TestClient
from src.gittxt_ui.app import app

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
        response = client.get(f"/download/{output_format}/test-output.{output_format}")
        assert response.status_code == 200, f"Failed to download {output_format} file."
        assert "content-disposition" in response.headers