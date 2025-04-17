import pytest
import httpx

@pytest.mark.asyncio
async def test_inspect_minimal():
    payload = {
        "repo_path": "https://github.com/sandy-sp/gittxt",
        "max_depth": 2
    }
    async with httpx.AsyncClient() as client:
        r = await client.post("http://127.0.0.1:8000/v1/inspect/", json=payload)
        print("INSPECT ERROR:", r.status_code, r.text)  
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "repo_tree" in data["data"]
