import os
import json
import shutil
import time
import pytest
from gittxt.scanner import Scanner

# Define expected directory paths inside `src/gittxt-outputs/`
SRC_DIR = os.path.dirname(__file__)  # `tests/`
OUTPUT_DIR = os.path.join(SRC_DIR, "../src/gittxt-outputs")
CACHE_DIR = os.path.join(OUTPUT_DIR, "cache")

@pytest.fixture(scope="function")
def clean_cache_dir():
    """Ensure the cache directory is clean before each test."""
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)  # Remove cache directory if it exists
    os.makedirs(CACHE_DIR, exist_ok=True)  # Recreate cache directory
    yield
    shutil.rmtree(CACHE_DIR)  # Cleanup after test

@pytest.fixture
def sample_files(tmp_path):
    """Create sample text files for testing."""
    file1 = tmp_path / "file1.py"
    file1.write_text("print('Hello from Python')\n")

    file2 = tmp_path / "file2.txt"
    file2.write_text("Hello World in text file\n")

    return [str(file1), str(file2)], str(tmp_path)

def test_first_time_scan(clean_cache_dir, sample_files):
    """Test first-time scan of a directory."""
    files, repo_path = sample_files
    scanner = Scanner(repo_name="test_repo", root_path=repo_path)
    scanned_files = scanner.scan_directory()

    assert len(scanned_files) == 2, "Not all files were scanned on first run"
    cache_file = os.path.join(CACHE_DIR, "test_repo_cache.json")
    assert os.path.exists(cache_file), "Cache file was not created"

def test_re_scan_without_changes(clean_cache_dir, sample_files):
    """Test scanning again without modifications (should skip unchanged files)."""
    files, repo_path = sample_files
    scanner = Scanner(repo_name="test_repo", root_path=repo_path)
    scanner.scan_directory()  # First scan
    start_time = time.time()
    scanned_files = scanner.scan_directory()  # Second scan (should be fast)
    end_time = time.time()

    assert len(scanned_files) == 0, "Unchanged files were not skipped"
    assert (end_time - start_time) < 1, "Scanning took too long for unchanged files"

def test_modify_file_and_re_scan(clean_cache_dir, sample_files):
    """Test modifying a file and ensuring cache detects it."""
    files, repo_path = sample_files
    scanner = Scanner(repo_name="test_repo", root_path=repo_path)
    scanner.scan_directory()  # First scan

    # Modify a file
    with open(files[0], "a") as f:
        f.write("\n# New Comment Added")

    scanned_files = scanner.scan_directory()  # Re-scan

    assert len(scanned_files) == 1, "Modified file was not detected"

def test_handle_corrupt_cache(clean_cache_dir, sample_files):
    """Test handling of a corrupt cache file."""
    files, repo_path = sample_files
    scanner = Scanner(repo_name="test_repo", root_path=repo_path)
    scanner.scan_directory()  # First scan

    # Corrupt the cache file
    cache_file = os.path.join(CACHE_DIR, "test_repo_cache.json")
    with open(cache_file, "w") as f:
        f.write("{corrupted_json}")  # Invalid JSON format

    # Re-scan after corruption
    scanner = Scanner(repo_name="test_repo", root_path=repo_path)  # Reload scanner
    scanned_files = scanner.scan_directory()

    assert len(scanned_files) == 2, "Scanner did not recover from corrupt cache"
    assert os.path.exists(cache_file), "Cache file should be recreated"


def test_exclude_files_by_pattern(clean_cache_dir, sample_files):
    """Test excluding files by pattern."""
    files, repo_path = sample_files
    scanner = Scanner(repo_name="test_repo", root_path=repo_path, exclude_patterns=[".py"])
    scanned_files = scanner.scan_directory()

    assert len(scanned_files) == 1, "Exclusion pattern did not work correctly"

def test_exclude_large_files(clean_cache_dir, tmp_path):
    """Test excluding files based on size."""
    small_file = tmp_path / "small.txt"
    small_file.write_text("This is a small file")

    large_file = tmp_path / "large.txt"
    large_file.write_text("X" * 10_000_000)  # Large file (10MB)

    files = [str(small_file), str(large_file)]
    scanner = Scanner(repo_name="test_repo", root_path=str(tmp_path), size_limit=5_000_000)  # 5MB limit
    scanned_files = scanner.scan_directory()

    # Use relative paths to match how scanner stores paths
    scanned_files = [os.path.basename(file) for file in scanned_files]

    assert "large.txt" not in scanned_files, "Large file was not excluded"
    assert "small.txt" in scanned_files, "Small file should not be excluded"