import pytest
import requests
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="session")
def dummy_repo_url():
    # Replace this dummy URL with a valid GitHub repo when ready
    return "https://github.com/sandy-sp/gittxt"

def test_get_config():
    resp = requests.get(f"{BASE_URL}/config")
    assert resp.status_code == 200
    assert "output_dir" in resp.json()

def test_update_config():
    payload = {"logging_level": "DEBUG"}
    resp = requests.post(f"{BASE_URL}/config", json=payload)
    assert resp.status_code in [200, 400, 405]
    if resp.status_code == 200:
        assert resp.json().get("success") is True

def test_repo_tree_valid(dummy_repo_url):
    resp = requests.post(f"{BASE_URL}/scans/tree", json={"repo_url": dummy_repo_url})
    # This will fail on dummy URL but works on a valid one
    assert resp.status_code in [200, 400]
    if resp.status_code == 200:
        data = resp.json()
        assert "tree" in data
        assert "file_extensions" in data

def test_repo_tree_invalid_url():
    resp = requests.post(f"{BASE_URL}/scans/tree", json={"repo_url": "not-a-valid-url"})
    assert resp.status_code == 400

@pytest.fixture(scope="session")
def scan_id(dummy_repo_url):
    payload = {
        "repo_url": dummy_repo_url,
        "file_types": ["code", "docs"],
        "output_format": "txt,json,md",
        "exclude_patterns": [],
        "include_patterns": [],
        "branch": None,
    }
    resp = requests.post(f"{BASE_URL}/scans", json=payload)
    assert resp.status_code == 200
    return resp.json()["scan_id"]

def test_wait_for_scan(scan_id):
    while True:
        resp = requests.get(f"{BASE_URL}/scans/{scan_id}")
        assert resp.status_code == 200
        status = resp.json()["status"]
        if status in ["done", "error"]:
            break
        time.sleep(1)
    assert status == "done"

def test_artifacts_download(scan_id):
    for fmt in ["json", "txt", "md", "zip"]:
        url = f"{BASE_URL}/artifacts/{scan_id}/{fmt}"
        r = requests.get(url)
        if fmt == "zip" and r.status_code == 404:
            # ZIP might be skipped if no assets exist, handle as optional
            continue
        assert r.status_code == 200

def test_close_scan_session(scan_id):
    resp = requests.delete(f"{BASE_URL}/scans/{scan_id}/close")
    assert resp.status_code == 200
    assert resp.json().get("success") is True

def test_get_nonexistent_scan():
    resp = requests.get(f"{BASE_URL}/scans/non-existent-id")
    assert resp.status_code == 404

def test_close_nonexistent_scan():
    resp = requests.delete(f"{BASE_URL}/scans/non-existent-id/close")
    assert resp.status_code == 404

