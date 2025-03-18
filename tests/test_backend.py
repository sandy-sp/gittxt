import pytest
import requests
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def scan_id_fixture():
    """
    1) Posts to /scans to start a new Gittxt scan.
    2) Returns the scan_id for use in subsequent tests.
    Ensures only one scan is started per session.
    """
    url = f"{BASE_URL}/scans"
    payload = {
        "repo_url": "https://github.com/sandy-sp/gittxt.git",
        "file_types": "code,docs",
        "output_format": "txt,json,md",
        "include_patterns": [],
        "exclude_patterns": [".git", "node_modules"],
        "size_limit": None,
        "branch": None,
    }
    resp = requests.post(url, json=payload)
    assert resp.status_code == 200, f"POST /scans => {resp.status_code}"
    data = resp.json()
    scan_id = data["scan_id"]
    print(f"[fixture:scan_id_fixture] Started scan => scan_id={scan_id}")
    return scan_id


def test_1_get_config():
    """Test GET /config => Should return the current Gittxt config."""
    url = f"{BASE_URL}/config"
    resp = requests.get(url)
    assert resp.status_code == 200, f"GET /config => {resp.status_code}"
    data = resp.json()
    print("test_1_get_config =>", data)
    assert isinstance(data, dict), "Expected a dict config"
    assert "output_dir" in data, "Missing 'output_dir' in config"


def test_2_update_config():
    """
    Test POST /config => Optionally update e.g. logging_level.
    If your endpoint is read-only, you may get 400 or 405, etc.
    """
    url = f"{BASE_URL}/config"
    payload = {"logging_level": "DEBUG"}  # Example
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print("test_2_update_config =>", data)
        assert data["success"] is True, "Expected success from config update"
        # Optionally confirm we got back an updated logging level
        updated_cfg = data.get("updated_config", {})
        assert updated_cfg.get("logging_level") == "DEBUG"
    else:
        # If the API doesn't allow updates, check for 400 or 405
        print("test_2_update_config => HTTP", resp.status_code, resp.text)
        assert resp.status_code in (400, 405)


def test_3_repo_tree():
    """Test POST /scans/tree => returns directory structure + file extensions."""
    url = f"{BASE_URL}/scans/tree"
    payload = {
        "repo_url": "https://github.com/sandy-sp/gittxt.git",
        "branch": None,
    }
    resp = requests.post(url, json=payload)
    assert resp.status_code == 200, f"POST /scans/tree => {resp.status_code}"
    data = resp.json()
    print("test_3_repo_tree =>", data)
    assert "tree" in data, "Missing 'tree' in /tree response"
    assert "file_extensions" in data, "Missing 'file_extensions' in /tree response"


def test_3a_repo_tree_invalid_url():
    """
    Test that passing an invalid repo URL yields an error.
    """
    url = f"{BASE_URL}/scans/tree"
    payload = {
        "repo_url": "not-a-valid-url",
        "branch": None,
    }
    resp = requests.post(url, json=payload)
    # Expect the backend to return 400 or an error
    assert resp.status_code >= 400, "Should fail on invalid URL"
    print("test_3a_repo_tree_invalid_url =>", resp.status_code, resp.text)


def test_4_wait_for_scan_done(scan_id_fixture):
    """
    Wait for the fixture-based scan to complete by polling GET /scans/{scan_id}.
    """
    scan_id = scan_id_fixture
    url = f"{BASE_URL}/scans/{scan_id}"

    # Poll until done/error
    while True:
        resp = requests.get(url)
        assert resp.status_code == 200, f"GET /scans/{scan_id} => {resp.status_code}"
        data = resp.json()
        status = data["status"]
        progress = data["progress"]
        print(f"Scan {scan_id} => status={status}, progress={progress}")

        if status in ["done", "error"]:
            break
        time.sleep(2)

    # If it's an error, fail the test
    assert status == "done", f"Scan ended with status={status}"
    print("Scan reached 'done' => good to retrieve artifacts.")


def test_5_artifacts_download(scan_id_fixture):
    """
    Check .json, .txt, .md, .zip from /artifacts/{scan_id}.
    Should pass if the scan has completed (from test_4_wait_for_scan_done).
    """
    scan_id = scan_id_fixture

    # JSON
    url_json = f"{BASE_URL}/artifacts/{scan_id}/json"
    rj = requests.get(url_json)
    if rj.status_code == 200:
        data = rj.json()
        print("Art JSON => top-level keys:", list(data.keys()))
        assert "repository_structure" in data, "Expected 'repository_structure' in JSON"
    else:
        print("Art JSON =>", rj.status_code, rj.text)

    # TXT
    url_txt = f"{BASE_URL}/artifacts/{scan_id}/txt"
    rt = requests.get(url_txt)
    if rt.status_code == 200:
        print("Art TXT => length:", len(rt.content))
        assert len(rt.content) > 0, "Expected some TXT content"
    else:
        print("Art TXT =>", rt.status_code, rt.text)

    # MD
    url_md = f"{BASE_URL}/artifacts/{scan_id}/md"
    rm = requests.get(url_md)
    if rm.status_code == 200:
        # Decode the raw response bytes to a string
        md_text = rm.content.decode("utf-8", errors="replace")
        print("Art MD => length:", len(md_text))
        # Confirm it contains a heading with the summary text
        assert "## 📊 Summary Report" in md_text, "Expected summary markdown in .md"
    else:
        print("Art MD =>", rm.status_code, rm.text)

    # ZIP
    url_zip = f"{BASE_URL}/artifacts/{scan_id}/zip"
    rz = requests.get(url_zip)
    if rz.status_code == 200:
        zip_file = Path(f"scan_{scan_id}_bundle.zip")
        zip_file.write_bytes(rz.content)
        print(f"Art ZIP => saved => {zip_file} size={zip_file.stat().st_size}")
        assert zip_file.stat().st_size > 0, "Zip file shouldn't be empty"
        # Clean up after the test
        zip_file.unlink()
    else:
        print("Art ZIP =>", rz.status_code, rz.text)

    # At least one artifact should have been HTTP 200 if everything is correct.

def test_6_close_session(scan_id_fixture):
    """
    DELETE /scans/{scan_id}/close => ephemeral cleanup
    """
    scan_id = scan_id_fixture
    url = f"{BASE_URL}/scans/{scan_id}/close"
    resp = requests.delete(url)
    assert resp.status_code == 200, f"DELETE /scans/{scan_id}/close => {resp.status_code}"
    data = resp.json()
    print("test_6_close_session =>", data)
    assert data["success"] is True, "Expected success from close"


def test_7_close_non_existent_scan():
    """
    Attempt to close a scan that doesn't exist => expect 404.
    """
    bogus_id = "12345-non-existent"
    url = f"{BASE_URL}/scans/{bogus_id}/close"
    resp = requests.delete(url)
    assert resp.status_code == 404, "Expected 404 for non-existent scan"
    data = resp.json()
    print("test_7_close_non_existent_scan =>", data)


def test_8_get_scan_info_non_existent():
    """
    GET /scans/{scan_id} for a scan that doesn't exist => expect 404.
    """
    bogus_id = "scan-not-found"
    url = f"{BASE_URL}/scans/{bogus_id}"
    resp = requests.get(url)
    assert resp.status_code == 404, "Expected 404 for non-existent scan"
    print("test_8_get_scan_info_non_existent =>", resp.status_code, resp.text)


@pytest.mark.skip(reason="Optional concurrency test. Enable if you want to verify queuing logic.")
def test_9_concurrent_scans():
    """
    Optional: We can test concurrency (since max concurrent scans=1).
    1) Start a first scan that sleeps a while (simulate a real or large repo).
    2) Start a second scan => should be queued until the first finishes.
    3) Wait for both to finish and confirm statuses (1: done, 2: done).
    """
    # Start first scan (maybe pass a big repo or add extra param to cause a slower scan).
    url = f"{BASE_URL}/scans"
    payload1 = {"repo_url": "https://github.com/sandy-sp/gittxt.git"}
    resp1 = requests.post(url, json=payload1)
    assert resp1.status_code == 200
    scan_id_1 = resp1.json()["scan_id"]

    # Start second scan
    payload2 = {"repo_url": "https://github.com/sandy-sp/gittxt.git"}
    resp2 = requests.post(url, json=payload2)
    assert resp2.status_code == 200
    scan_id_2 = resp2.json()["scan_id"]

    # Poll both until done:
    for s_id in (scan_id_1, scan_id_2):
        check_url = f"{BASE_URL}/scans/{s_id}"
        while True:
            r = requests.get(check_url)
            assert r.status_code == 200
            sdata = r.json()
            if sdata["status"] in ["done", "error"]:
                break
            time.sleep(2)

        # Validate final
        assert sdata["status"] == "done", f"Scan {s_id} ended with {sdata['status']}"

    # Cleanup each
    for s_id in (scan_id_1, scan_id_2):
        close_url = f"{BASE_URL}/scans/{s_id}/close"
        requests.delete(close_url)


@pytest.mark.skip(reason="Requires an async test client & WebSocket library such as 'websockets' or 'pytest-asyncio'.")
async def test_10_websocket_progress():
    """
    Optional: Example for testing the WS progress endpoint. 
    You'd need an async test client that can open websockets, e.g. using pytest-asyncio.
    """
    import websockets

    # 1) Start a scan
    scan_url = f"{BASE_URL}/scans"
    payload = {"repo_url": "https://github.com/sandy-sp/gittxt.git"}
    resp = requests.post(scan_url, json=payload)
    assert resp.status_code == 200
    s_id = resp.json()["scan_id"]

    # 2) Open WS to track progress
    ws_url = f"ws://127.0.0.1:8000/wsprogress/ws/{s_id}"
    async with websockets.connect(ws_url) as ws:
        while True:
            msg = await ws.recv()
            # parse JSON, e.g. with json.loads(msg)
            # check progress status or event == "done"
            # break when done

    # 3) Optionally confirm final status
    info_url = f"{BASE_URL}/scans/{s_id}"
    final = requests.get(info_url)
    assert final.json()["status"] == "done"

    # 4) Cleanup
    close_url = f"{BASE_URL}/scans/{s_id}/close"
    requests.delete(close_url)
