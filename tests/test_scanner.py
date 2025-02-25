import os
import pytest
from gittxt.scanner import Scanner

@pytest.fixture
def test_directory(tmp_path):
    """Set up a temporary directory with sample files."""
    test_dir = tmp_path / "test_repo"
    test_dir.mkdir()

    # Create sample files
    (test_dir / "file1.py").write_text("print('Hello')")
    (test_dir / "file2.txt").write_text("Hello World")
    (test_dir / "test_exclude.py").write_text("Excluded file")
    (test_dir / "large_file.log").write_text("X" * 1000000)  # Large file

    return test_dir

def test_scan_all_files(test_directory):
    """Test if scanner detects all files."""
    scanner = Scanner(root_path=str(test_directory))
    files = scanner.scan_directory()
    assert len(files) == 4  # Should find all files

def test_scan_with_exclude(test_directory):
    """Test excluding files by pattern."""
    scanner = Scanner(root_path=str(test_directory), exclude_patterns=["test_exclude.py", ".log"])
    files = scanner.scan_directory()
    assert len(files) == 2  # Should exclude test_exclude.py and large_file.log

def test_scan_with_include(test_directory):
    """Test including only specific file types."""
    scanner = Scanner(root_path=str(test_directory), include_patterns=[".py"])
    files = scanner.scan_directory()
    assert len(files) == 2  # Should include only .py files
