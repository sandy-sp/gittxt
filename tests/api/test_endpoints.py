import pytest
import subprocess
import httpx
import time
import os
import signal
from pathlib import Path

API_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="session", autouse=True)
def start_api():
    # Launch API subprocess
    proc = subprocess.Popen(
        ["gittxt", "api", "run", "--reload", "--log-level", "error"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid  # So we can kill the process group
    )
    time.sleep(3)  # Wait for API to boot up (or better: check health endpoint)
    yield
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)  # Clean shutdown

@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_inspect_repo():
    async with httpx.AsyncClient() as client:
        payload = {
            "repo_path": "https://github.com/sandy-sp/gittxt",
        }
        r = await client.post(f"{API_URL}/inspect/", json=payload)
        assert r.status_code == 200
        assert "repository" in r.json()
        global test_summary  # Store for downstream scan
        test_summary = r.json()

@pytest.mark.asyncio
async def test_scan_repo():
    async with httpx.AsyncClient() as client:
        payload = {
            "repo_path": "https://github.com/sandy-sp/gittxt",
            "lite": True,
            "create_zip": True
        }
        r = await client.post(f"{API_URL}/scan/", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "scan_id" in data
        global scan_id
        scan_id = data["scan_id"]

@pytest.mark.asyncio
async def test_summary():
    assert scan_id
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}/summary/{scan_id}")
        assert r.status_code == 200
        assert "summary" in r.json() or "files" in r.json()

@pytest.mark.asyncio
async def test_download_txt():
    assert scan_id
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}/download/{scan_id}?format=txt")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/plain")

@pytest.mark.asyncio
async def test_cleanup():
    assert scan_id
    async with httpx.AsyncClient() as client:
        r = await client.delete(f"{API_URL}/cleanup/{scan_id}")
        assert r.status_code == 200
        assert "Deleted" in r.json()["message"]

@pytest.mark.asyncio
async def test_upload_zip():
    zip_path = Path("tests/api/test_repo.zip")  # Make sure it exists
    assert zip_path.exists()
    async with httpx.AsyncClient() as client:
        with zip_path.open("rb") as f:
            files = {"file": ("sample_repo.zip", f, "application/zip")}
            r = await client.post(f"{API_URL}/upload/?lite=true", files=files)
        assert r.status_code == 200
        assert "scan_id" in r.json()
