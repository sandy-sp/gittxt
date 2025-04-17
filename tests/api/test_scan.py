import pytest
import httpx

scan_id = None

@pytest.mark.asyncio
async def test_scan_lite():
    global scan_id
    payload = {
        "repo_path": "https://github.com/sandy-sp/gittxt",
        "lite": True,
        "create_zip": True
    }
    async with httpx.AsyncClient() as client:
        r = await client.post("http://127.0.0.1:8000/v1/scan", json=payload)
        assert r.status_code == 201
        scan_id = r.json()["data"]["scan_id"]
        assert scan_id
