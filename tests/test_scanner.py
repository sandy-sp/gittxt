from gittxt.scanner import Scanner
from pathlib import Path

def test_scanner_basic_scan(test_repo):
    scanner = Scanner(
        root_path=test_repo,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=None,
        file_types=["all"],
        progress=False
    )
    files, tree = scanner.scan_directory()
    assert len(files) >= 4  # src/example.py, docs/README.md, data/sample.csv, image.png
    assert "src" in tree


def test_scanner_exclude(test_repo):
    scanner = Scanner(
        root_path=test_repo,
        include_patterns=[],
        exclude_patterns=["*.png"],
        size_limit=None,
        file_types=["all"],
        progress=False
    )
    files, _ = scanner.scan_directory()
    pngs = [f for f in files if f.suffix == ".png"]
    assert len(pngs) == 0


def test_scanner_include_pattern(test_repo):
    scanner = Scanner(
        root_path=test_repo,
        include_patterns=["*.md"],
        exclude_patterns=[],
        size_limit=None,
        file_types=["all"],
        progress=False
    )
    files, _ = scanner.scan_directory()
    assert all(".md" in str(f) for f in files)
    assert len(files) == 1
