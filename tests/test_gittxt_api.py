import asyncio
import httpx

BASE_URL = "http://127.0.0.1:8000"

sample_payload = {
    "repo_url": "https://github.com/sandy-sp/gittxt",
    "output_format": ["txt", "json"],
    "create_zip": True,
    "lite_mode": True,
    "tree_depth": 2,
    "exclude_patterns": ["*.png", "*.csv"]
}

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
        assert "summary" not in data  # simplified response
        assert "output_files" in data

async def test_async_scan_and_status():
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
                print("✅ Async Scan Result:", result_resp.json()["repo_name"])
                break
            elif data["status"] == "failed":
                print("❌ Failed Scan:", data.get("error"))
                break

async def test_invalid_repo_url():
    payload = sample_payload.copy()
    payload["repo_url"] = "ftp://invalid.url"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.post(f"{BASE_URL}/scan", json=payload)
        assert r.status_code == 422
        print("✅ Rejected invalid repo_url")

async def test_unsupported_output_format():
    payload = sample_payload.copy()
    payload["output_format"] = ["txt", "xml"]
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.post(f"{BASE_URL}/scan", json=payload)
        assert r.status_code == 422
        print("✅ Rejected unsupported output_format")

async def test_invalid_task_id_status():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(f"{BASE_URL}/scan/status/non-existent-id-123")
        assert r.status_code == 404
        print("✅ 404 on invalid task_id")

async def test_missing_output_dir_download():
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(f"{BASE_URL}/download/zip?output_dir=/fake/path/to/nothing")
        assert r.status_code == 404
        print("✅ 404 on missing ZIP file")

async def run_all_tests():
    await test_health()
    await test_sync_scan()
    await test_async_scan_and_status()
    await test_invalid_repo_url()
    await test_unsupported_output_format()
    await test_invalid_task_id_status()
    await test_missing_output_dir_download()

if __name__ == "__main__":
    asyncio.run(run_all_tests())
