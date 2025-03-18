import pytest
import requests
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="session")
def scan_id_fixture():
    """
    A fixture that:
      1) Posts to /scans to start a new Gittxt scan.
      2) Returns the scan_id for use in subsequent tests.
    This ensures we only start the scan once per session.
    """
    # Start the scan with typical sample data
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

    # Return the scan_id so other tests can use it
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
    # etc.

def test_2_update_config():
    """
    Test POST /config => Optionally update e.g. logging_level.
    If your endpoint is read-only, you may get a 400 or 405, 
    which is also acceptable if that's expected behavior.
    """
    url = f"{BASE_URL}/config"
    payload = {"logging_level": "DEBUG"}  # Example
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        print("test_2_update_config =>", data)
        assert data["success"] is True, "Expected success from config update"
    else:
        print("test_2_update_config => HTTP", resp.status_code, resp.text)
        # If your config doesn't allow updates, 
        # you can assert resp.status_code == 400 or 405, if that's your design.

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

def test_4_wait_for_scan_done(scan_id_fixture):
    """
    We rely on the fixture 'scan_id_fixture' to create a scan.
    We'll poll GET /scans/{scan_id} until it's done or error.
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
    Should pass if the scan has completed.
    """
    scan_id = scan_id_fixture
    # 1) JSON
    url_json = f"{BASE_URL}/artifacts/{scan_id}/json"
    rj = requests.get(url_json)
    if rj.status_code == 200:
        data = rj.json()
        print("Art JSON => top-level keys:", list(data.keys()))
    else:
        print("Art JSON =>", rj.status_code, rj.text)

    # 2) TXT
    url_txt = f"{BASE_URL}/artifacts/{scan_id}/txt"
    rt = requests.get(url_txt)
    if rt.status_code == 200:
        print("Art TXT => length:", len(rt.content))
    else:
        print("Art TXT =>", rt.status_code, rt.text)

    # 3) MD
    url_md = f"{BASE_URL}/artifacts/{scan_id}/md"
    rm = requests.get(url_md)
    if rm.status_code == 200:
        print("Art MD => length:", len(rm.content))
    else:
        print("Art MD =>", rm.status_code, rm.text)

    # 4) ZIP
    url_zip = f"{BASE_URL}/artifacts/{scan_id}/zip"
    rz = requests.get(url_zip)
    if rz.status_code == 200:
        zip_file = Path(f"scan_{scan_id}_bundle.zip")
        zip_file.write_bytes(rz.content)
        print(f"Art ZIP => saved => {zip_file} size={zip_file.stat().st_size}")
    else:
        print("Art ZIP =>", rz.status_code, rz.text)

    # We'll do minimal asserts: at least one artifact should be 200
    # or "done" might have been too quick, or you can add more robust checks.

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
    # Optional: check the ephemeral output dir is actually gone, 
    # but that might require knowledge of the path from previous calls.
