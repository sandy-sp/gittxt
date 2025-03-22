import time

def test_tree_endpoint(api_client, test_repo):
    res = api_client.post("/scans/tree", json={"repo_url": str(test_repo)})
    assert res.status_code == 200
    json_data = res.json()
    assert "tree" in json_data
    assert "file_extensions" in json_data
    assert isinstance(json_data["file_extensions"], list)


def test_scan_end_to_end(api_client, test_repo):
    # Step 1: Launch scan
    payload = {
        "repo_url": str(test_repo),
        "file_types": ["code", "docs", "csv"],
        "output_format": "txt,json,md",
        "create_zip": True
    }
    res = api_client.post("/scans", json=payload)
    assert res.status_code == 200
    scan_id = res.json()["scan_id"]

    # Step 2: Poll scan status
    for _ in range(10):
        info = api_client.get(f"/scans/{scan_id}").json()
        if info.get("status") == "done":
            break
        time.sleep(1)

    assert info["status"] == "done"
    assert info["file_count"] > 0
    assert "artifacts" in info

    # Step 3: Artifact retrieval (txt, json, md, zip)
    for fmt in ["txt", "json", "md", "zip"]:
        r = api_client.get(info["artifacts"][fmt])
        assert r.status_code == 200

    # Step 4: Cleanup session
    close = api_client.delete(f"/scans/{scan_id}/close")
    assert close.status_code == 200
    assert close.json()["success"] is True


def test_config_get_and_update(api_client):
    res = api_client.get("/config/")
    assert res.status_code == 200
    data = res.json()
    assert "output_dir" in data
    assert "file_types" in data

    # Test a partial update (toggle auto_zip)
    update = api_client.post("/config/", json={"auto_zip": True})
    assert update.status_code == 200
    assert update.json()["success"] is True
