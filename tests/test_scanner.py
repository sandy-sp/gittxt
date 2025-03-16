import pytest
import sqlite3
from pathlib import Path
from unittest.mock import patch
from gittxt.scanner import Scanner

@pytest.fixture(scope="function")
def setup_test_files(tmp_path):
    test_dir = tmp_path / "test-repo"
    test_dir.mkdir()
    (test_dir / "file1.py").write_text("print('Hello, world!')", encoding="utf-8")
    (test_dir / "file2.md").write_text("# Sample Markdown", encoding="utf-8")
    (test_dir / "file3.mp4").write_bytes(b"\x00\x01\x02\x03")
    (test_dir / "file4.tar.gz").write_bytes(b"\x1f\x8b\x08\x00")
    return test_dir

@pytest.fixture(scope="function")
def clean_cache(tmp_path):
    cache_dir = tmp_path / "gittxt-outputs" / "cache"
    if cache_dir.exists():
        for db_file in cache_dir.glob("*"):
            db_file.unlink()
    cache_dir.mkdir(parents=True, exist_ok=True)

def test_scan_directory_identifies_text_files(setup_test_files, clean_cache):
    scanner = Scanner(root_path=setup_test_files)
    valid_files, _ = scanner.scan_directory()
    valid_basenames = [Path(f).name for f in valid_files]
    assert "file1.py" in valid_basenames
    assert "file2.md" in valid_basenames

def test_exclude_non_text_files(setup_test_files, clean_cache):
    scanner = Scanner(root_path=setup_test_files)
    valid_files, _ = scanner.scan_directory()
    valid_basenames = [Path(f).name for f in valid_files]
    assert "file3.mp4" not in valid_basenames
    assert "file4.tar.gz" not in valid_basenames

def test_include_exclude_patterns(setup_test_files, clean_cache):
    scanner = Scanner(
        root_path=setup_test_files,
        include_patterns=[".py"],
        exclude_patterns=["file1.py"]
    )
    valid_files, _ = scanner.scan_directory()
    valid_basenames = [Path(f).name for f in valid_files]
    assert "file1.py" not in valid_basenames
    assert "file2.md" not in valid_basenames

def test_size_limit_exclusion(setup_test_files, clean_cache):
    large_file = setup_test_files / "large.txt"
    large_file.write_text("A" * 1000000, encoding="utf-8")
    scanner = Scanner(root_path=setup_test_files, size_limit=500000)
    valid_files, _ = scanner.scan_directory()
    valid_basenames = [Path(f).name for f in valid_files]
    assert "large.txt" not in valid_basenames

def test_caching_prevents_rescanning(setup_test_files, clean_cache):
    scanner = Scanner(root_path=setup_test_files)
    scanner.clear_cache()
    valid_files, _ = scanner.scan_directory()

    conn = sqlite3.connect(scanner.CACHE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM file_cache")
    cached_count = cursor.fetchone()[0]
    conn.close()

    assert cached_count == len(valid_files)

    # Second scan to test cache
    valid_files_second, _ = scanner.scan_directory()
    conn = sqlite3.connect(scanner.CACHE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM file_cache")
    cached_count_after = cursor.fetchone()[0]
    conn.close()

    assert cached_count_after == cached_count

@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_mime_type_check(mock_mime, setup_test_files, clean_cache):
    scanner = Scanner(root_path=setup_test_files)
    valid_files, _ = scanner.scan_directory()
    valid_basenames = [Path(f).name for f in valid_files]
    assert "file1.py" in valid_basenames
    assert "file3.mp4" not in valid_basenames

def test_docs_only(setup_test_files, clean_cache):
    scanner = Scanner(root_path=setup_test_files, docs_only=True)
    valid_files, _ = scanner.scan_directory()
    valid_basenames = [Path(f).name for f in valid_files]
    assert "file2.md" in valid_basenames
    assert "file1.py" not in valid_basenames

def test_auto_filter(setup_test_files, clean_cache):
    scanner = Scanner(root_path=setup_test_files, auto_filter=True)
    valid_files, _ = scanner.scan_directory()
    valid_basenames = [Path(f).name for f in valid_files]
    assert "file1.py" in valid_basenames
    assert "file2.md" in valid_basenames
    assert "file3.mp4" not in valid_basenames
    assert "file4.tar.gz" not in valid_basenames
