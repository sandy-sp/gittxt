import pytest
import httpx

@pytest.mark.asyncio
async def test_download(scan_id):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"http://127.0.0.1:8000/v1/download/{scan_id}?format=txt")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/plain")
