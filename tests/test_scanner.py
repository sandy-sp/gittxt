import pytest
from pathlib import Path
from gittxt.core.scanner import Scanner

TEST_REPO = Path("test_repo")

def test_scanner_with_default_config():
    scanner = Scanner(root_path=TEST_REPO)
    included = scanner.scan_directory()

    assert isinstance(included, list)
    assert any("script.py" in str(f) for f in included)
    assert all("node_modules" not in str(f) for f in included)
    assert all(not f.name.endswith(".zip") for f in included)
    assert all(f.suffix not in [".zip", ".png", ".dat"] for f in included)

def test_scanner_skipped_reasons():
    scanner = Scanner(root_path=TEST_REPO)
    included = scanner.scan_directory()
    skipped = scanner.skipped_files

    # Test: large file should be skipped
    assert any("script_large.py" in str(p) for p, reason in skipped)
    
    # Test: archive excluded
    reasons = [r for _, r in skipped]
    assert "exclude pattern" in reasons or "non-textual" in reasons
    assert any("non-textual" in r for r in reasons)

def test_scanner_with_include_pattern():
    scanner = Scanner(root_path=TEST_REPO, include_patterns=["*.txt"])
    included = scanner.scan_directory()
    skipped = scanner.skipped_files

    assert any("included.txt" in str(f) for f in included)
    assert all(f.name.endswith(".txt") for f in included)

def test_scanner_with_exclude_pattern():
    scanner = Scanner(root_path=TEST_REPO, exclude_patterns=["*.csv", "*.min.js"])
    included = scanner.scan_directory()
    assert all(not f.name.endswith(".csv") and not f.name.endswith(".min.js") for f in included)
