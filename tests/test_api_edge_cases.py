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
    assert res.status_code == 400 or res.status_code == 422


def test_ws_invalid_scan_id(api_client):
    with pytest.raises(WebSocketDisconnect):
        with api_client.websocket_connect("/wsprogress/ws/invalid-scan-id") as ws:
            ws.receive_json()


def test_artifact_404_before_scan_completion(api_client, test_repo):
    # Launch scan
    payload = {"repo_url": str(test_repo), "file_types": ["code", "docs"]}
    res = api_client.post("/scans", json=payload)
    assert res.status_code == 200
    scan_id = res.json()["scan_id"]

    # Immediately try artifact download before completion
    artifact_url = f"/artifacts/{scan_id}/txt"
    r = api_client.get(artifact_url)
    assert r.status_code == 404

    # Cleanup
    api_client.delete(f"/scans/{scan_id}/close")
