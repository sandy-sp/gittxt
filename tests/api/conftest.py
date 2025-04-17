import pytest
import httpx
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def scan_id():
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/v1/scan/", json={
            "repo_path": "https://github.com/sandy-sp/gittxt",
            "lite": True,
            "create_zip": True
        })
        assert response.status_code == 201
        return response.json()["data"]["scan_id"]
