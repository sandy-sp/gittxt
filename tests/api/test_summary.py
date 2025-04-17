import pytest
import httpx

@pytest.mark.asyncio
async def test_summary(scan_id):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"http://127.0.0.1:8000/v1/summary/{scan_id}")
        assert r.status_code == 200
        assert "data" in r.json()
