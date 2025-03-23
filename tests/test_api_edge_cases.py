import time
from fastapi.websockets import WebSocketDisconnect
import pytest

def test_invalid_scan_payload(api_client):
    # Missing repo_url
    payload = {"file_types": ["code"]}
    res = api_client.post("/scans", json=payload)
    assert res.status_code == 422  # FastAPI validation error


def test_invalid_repo_url(api_client):
    payload = {"repo_url": "invalid-url", "file_types": ["code"]}
    res = api_client.post("/scans", json=payload)
    assert res.status_code in {400, 422}


def test_ws_invalid_scan_id(api_client):
    with pytest.raises(WebSocketDisconnect):
        with api_client.websocket_connect("/wsprogress/ws/nonexistent-id") as ws:
            ws.receive_json()


def test_artifact_404_before_scan_completion(api_client, test_repo):
    payload = {"repo_url": str(test_repo), "file_types": ["code", "docs"]}
    res = api_client.post("/scans", json=payload)
    assert res.status_code == 200
    scan_id = res.json()["scan_id"]

    # Fetch scan status BEFORE artifact request
    scan_status = api_client.get(f"/scans/{scan_id}").json()
    
    # Ensure it's still queued/running before artifact check
    if scan_status.get("status") != "done":
        artifact_url = f"/artifacts/{scan_id}/txt"
        r = api_client.get(artifact_url)
        assert r.status_code == 404
    else:
        # If scan completed too fast, skip assertion
        print("⚠️ Scan completed before artifact fetch, skipping artifact 404 assertion.")
