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
def scan_id(event_loop):
    return event_loop.run_until_complete(_get_scan_id())

async def _get_scan_id():
    async with httpx.AsyncClient() as client:
        response = await client.post("http://127.0.0.1:8000/v1/scan/", json={
            "repo_path": "https://github.com/sandy-sp/gittxt",
            "lite": True,
            "create_zip": True
        })
        assert response.status_code == 201
        return response.json()["data"]["scan_id"]

@pytest.fixture(scope="session", autouse=True)
def auto_cleanup(scan_id):
    yield
    import httpx
    import asyncio
    async def _cleanup():
        async with httpx.AsyncClient() as client:
            await client.delete(f"http://127.0.0.1:8000/v1/cleanup/{scan_id}")
    asyncio.get_event_loop().run_until_complete(_cleanup())
