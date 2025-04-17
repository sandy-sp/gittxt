import pytest
import httpx

@pytest.mark.asyncio
async def test_cleanup(scan_id):
    scan_id = await scan_id  # Await the fixture
    async with httpx.AsyncClient() as client:
        r = await client.delete(f"http://127.0.0.1:8000/v1/cleanup/{scan_id}")
        assert r.status_code == 200
        assert "Deleted" in r.json()["message"]
