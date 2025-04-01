from fastapi.testclient import TestClient
from src.gittxt_api.main import app

client = TestClient(app)

def test_scan_repo_invalid_url():
    response = client.post("/scan", json={"repo_url": "invalid-url"})
    assert response.status_code == 400
    assert "Invalid input" in response.json()["detail"]

def test_scan_repo_unauthorized():
    response = client.post("/scan", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"

def test_get_scan_summary_pagination():
    response = client.get("/scan/test-scan-id?page=1&page_size=2")
    assert response.status_code == 200
    assert "files" in response.json()
    assert response.json()["page"] == 1
    assert response.json()["page_size"] == 2
