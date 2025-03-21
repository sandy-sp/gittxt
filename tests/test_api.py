import time

def test_tree_endpoint(api_client, test_repo):
    res = api_client.post("/scans/tree", json={"repo_url": str(test_repo)})
    assert res.status_code == 200
    assert "tree" in res.json()
    assert "file_extensions" in res.json()


def test_scan_workflow(api_client, test_repo):
    # 1. Launch scan
    payload = {
        "repo_url": str(test_repo),
        "file_types": ["code", "docs", "csv"],
        "output_format": "txt,json,md",
        "create_zip": True
    }
    res = api_client.post("/scans", json=payload)
    assert res.status_code == 200
    scan_id = res.json()["scan_id"]

    # 2. Poll until done
    for _ in range(10):
        info = api_client.get(f"/scans/{scan_id}").json()
        if info.get("status") == "done":
            break
        time.sleep(1)

    assert info["status"] == "done"
    assert info["file_count"] > 0
    assert "artifacts" in info

    # 3. Validate artifacts
    for fmt in ["txt", "json", "md", "zip"]:
        r = api_client.get(info["artifacts"][fmt])
        assert r.status_code == 200

    # 4. Cleanup session
    close = api_client.delete(f"/scans/{scan_id}/close")
    assert close.status_code == 200
    assert close.json()["success"] is True
