import pytest
import subprocess
import os
import signal
import time
import httpx

@pytest.fixture(scope="session", autouse=True)
def start_api():
    proc = subprocess.Popen(
        ["gittxt", "api", "run", "--reload", "--log-level", "error"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    time.sleep(3)
    yield
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

@pytest.fixture(scope="session")
async def scan_id():
    payload = {
        "repo_path": "https://github.com/sandy-sp/gittxt",
        "lite": True,
        "create_zip": True
    }
    async with httpx.AsyncClient() as client:
        r = await client.post("http://127.0.0.1:8000/v1/scan/", json=payload)
        return r.json()["data"]["scan_id"]
