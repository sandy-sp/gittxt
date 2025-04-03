import asyncio
import httpx
from pathlib import Path
from typing import Optional

BASE_URL = "http://127.0.0.1:8000"

sample_payload = {
    "repo_url": "https://github.com/sandy-sp/gittxt",
    "output_format": ["txt", "json"],
    "create_zip": True,
    "lite_mode": True,
    "tree_depth": 2,
    "exclude_patterns": ["*.png", "*.csv"],
}

# Shared state
last_output_dir = None
last_output_files = []


async def test_health():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(f"{BASE_URL}/health")
        assert r.status_code == 200
        print("✅ Health Check:", r.json())


async def test_sync_scan():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.post(f"{BASE_URL}/scan", json=sample_payload)
        assert r.status_code == 200
        data = r.json()
        print("✅ Sync Scan Completed")
        print("Output Dir:", data.get("output_dir"))
        assert "output_files" in data and isinstance(data["output_files"], list)
        assert isinstance(data.get("repo_name"), str)
        assert isinstance(data.get("total_files"), int)
        assert isinstance(data.get("total_size_bytes"), int)
        assert isinstance(data.get("estimated_tokens"), int)
        assert isinstance(data.get("file_type_breakdown"), dict)
        assert isinstance(data.get("tokens_by_type"), dict)
        assert isinstance(data.get("skipped_files"), list)


async def test_async_scan_and_status():
    global last_output_dir, last_output_files
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.post(f"{BASE_URL}/scan/async", json=sample_payload)
        assert r.status_code == 200
        task_id = r.json()["task_id"]
        print("🚀 Async Task Started:", task_id)

        for _ in range(30):
            await asyncio.sleep(2)
            status_resp = await client.get(f"{BASE_URL}/scan/status/{task_id}")
            data = status_resp.json()
            print("📡 Status:", data["status"])
            if data["status"] == "completed":
                result_resp = await client.get(f"{BASE_URL}/scan/result/{task_id}")
                assert result_resp.status_code == 200
                result_data = result_resp.json()
                print("✅ Async Scan Result:", result_data["repo_name"])
                last_output_dir = result_data["output_dir"]
                last_output_files = result_data["output_files"]
                assert isinstance(last_output_files, list)
                assert isinstance(result_data.get("total_files"), int)
                break
            elif data["status"] == "failed":
                print("❌ Failed Scan:", data.get("error"))
                break


async def test_directory_tree():
    if not last_output_dir:
        print("⚠️  Skipping tree test: no output_dir available")
        return
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(
            f"{BASE_URL}/scan/tree", params={"output_dir": last_output_dir}
        )
        assert r.status_code == 200
        data = r.json()
        print("✅ Directory Tree Root:", data.get("root"))
        assert "tree" in data


def find_file_recursive(output_dir: Path, file_name: str) -> Optional[Path]:
    for path in output_dir.rglob("*"):
        if path.name == file_name and path.is_file():
            return path
    return None


@router.get("/download")
def download_output_file(output_dir: str = Query(...), file_name: str = Query(...)):
    base_path = Path(output_dir).resolve()
    target_file = find_file_recursive(base_path, file_name)

    if not target_file or not target_file.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {file_name}")

    return FileResponse(
        path=str(target_file),
        filename=target_file.name,
        media_type=_guess_mime_type(target_file),
    )


async def test_task_list():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(f"{BASE_URL}/scan/list")
        assert r.status_code == 200
        tasks = r.json()
        print(f"✅ Task List Count: {len(tasks)}")
        assert isinstance(tasks, list)


async def test_invalid_repo_url():
    payload = sample_payload.copy()
    payload["repo_url"] = "ftp://invalid.url"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.post(f"{BASE_URL}/scan", json=payload)
        assert r.status_code == 422 or r.status_code == 400
        print("✅ Rejected invalid repo_url")


async def test_unsupported_output_format():
    payload = sample_payload.copy()
    payload["output_format"] = ["txt", "xml"]
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.post(f"{BASE_URL}/scan", json=payload)
        assert r.status_code == 422 or r.status_code == 400
        print("✅ Rejected unsupported output_format")


async def test_invalid_task_id_status():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(f"{BASE_URL}/scan/status/non-existent-id-123")
        assert r.status_code == 404
        print("✅ 404 on invalid task_id")


async def test_missing_output_file_download():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(
            f"{BASE_URL}/download",
            params={"output_dir": "/fake/path/to/nothing", "file_name": "fake.zip"},
        )
        assert r.status_code == 404
        print("✅ 404 on missing file in download endpoint")


async def run_all_tests():
    await test_health()
    await test_sync_scan()
    await test_async_scan_and_status()
    await test_directory_tree()
    await test_download_output_file()
    await test_task_list()
    await test_invalid_repo_url()
    await test_unsupported_output_format()
    await test_invalid_task_id_status()
    await test_missing_output_file_download()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
