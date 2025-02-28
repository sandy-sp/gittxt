import pytest
import os
import mimetypes
import sqlite3
from unittest.mock import patch, MagicMock
from gittxt.scanner import Scanner

# Define test parameters
TEST_SCAN_DIR = os.path.join("tests", "test-scan-dir")
TEST_CACHE_DB = os.path.join("tests", "gittxt-outputs", "cache", "scan_cache.db")

@pytest.fixture(scope="function")
def setup_test_files(tmp_path):
    """Create a temporary directory with mock text and non-text files."""
    test_dir = tmp_path / "test-repo"
    test_dir.mkdir()

    # Create text files
    (test_dir / "file1.py").write_text("print('Hello, world!')", encoding="utf-8")
    (test_dir / "file2.md").write_text("# Sample Markdown", encoding="utf-8")

    # Create non-text files
    (test_dir / "file3.mp4").write_bytes(b"\x00\x01\x02\x03")
    (test_dir / "file4.tar.gz").write_bytes(b"\x1f\x8b\x08\x00")

    return test_dir

@pytest.fixture(scope="function")
def clean_cache():
    """Ensure the cache database is clean before each test."""
    if os.path.exists(TEST_CACHE_DB):
        os.remove(TEST_CACHE_DB)

def test_scan_directory_identifies_text_files(setup_test_files, clean_cache):
    """Ensure directory scanning correctly identifies valid text files."""
    scanner = Scanner(root_path=str(setup_test_files))
    valid_files, _ = scanner.scan_directory()

    assert "file1.py" in [os.path.basename(f) for f in valid_files]
    assert "file2.md" in [os.path.basename(f) for f in valid_files]

def test_exclude_non_text_files(setup_test_files, clean_cache):
    """Ensure non-text files are properly excluded from scanning."""
    scanner = Scanner(root_path=str(setup_test_files))
    valid_files, _ = scanner.scan_directory()

    assert "file3.mp4" not in [os.path.basename(f) for f in valid_files]
    assert "file4.tar.gz" not in [os.path.basename(f) for f in valid_files]

def test_include_exclude_patterns(setup_test_files, clean_cache):
    """Test if --include and --exclude patterns work correctly."""
    scanner = Scanner(
        root_path=str(setup_test_files),
        include_patterns=[".py"],
        exclude_patterns=["file1.py"]
    )
    valid_files, _ = scanner.scan_directory()

    assert "file1.py" not in [os.path.basename(f) for f in valid_files]  # Excluded
    assert "file2.md" not in [os.path.basename(f) for f in valid_files]  # Not included

def test_size_limit_exclusion(setup_test_files, clean_cache):
    """Ensure files exceeding --size-limit are skipped."""
    large_file = setup_test_files / "large.txt"
    large_file.write_text("A" * 1000000, encoding="utf-8")  # 1MB file

    scanner = Scanner(root_path=str(setup_test_files), size_limit=500000)
    valid_files, _ = scanner.scan_directory()

    assert "large.txt" not in [os.path.basename(f) for f in valid_files]

def test_caching_prevents_rescanning(setup_test_files, clean_cache):
    """Ensure caching prevents rescanning unchanged files."""
    scanner = Scanner(root_path=str(setup_test_files))
    valid_files, _ = scanner.scan_directory()

    # First scan should add files to cache
    conn = sqlite3.connect(scanner.CACHE_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM file_cache")
    cached_count = cursor.fetchone()[0]
    conn.close()

    assert cached_count == len(valid_files)

    # Second scan should not rescan unchanged files
    valid_files, _ = scanner.scan_directory()
    assert len(valid_files) == cached_count  # No additional files scanned

@patch("mimetypes.guess_type", return_value=("text/plain", None))
def test_mime_type_check(mock_mime, setup_test_files, clean_cache):
    """Ensure MIME type detection correctly classifies text files."""
    scanner = Scanner(root_path=str(setup_test_files))
    valid_files, _ = scanner.scan_directory()

    assert "file1.py" in [os.path.basename(f) for f in valid_files]
    assert "file3.mp4" not in [os.path.basename(f) for f in valid_files]
