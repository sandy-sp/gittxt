import pytest
import httpx
from pathlib import Path
import subprocess

@pytest.mark.asyncio
async def test_upload_zip():
    zip_path = Path("tests/api/test_repo.zip")
    if not zip_path.exists():
        subprocess.run(["python", "tests/api/generate_test_repo.py"], check=True)

    with zip_path.open("rb") as f:
        files = {"file": ("repo.zip", f, "application/zip")}
        async with httpx.AsyncClient() as client:
            r = await client.post("http://127.0.0.1:8000/v1/upload/?lite=true/", files=files)
            assert r.status_code == 201
            assert "scan_id" in r.json()["data"]
