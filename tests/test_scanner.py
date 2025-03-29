import pytest
from pathlib import Path
from gittxt.core.scanner import Scanner
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT

TEST_REPO = Path("tests/test_repo")

@pytest.mark.asyncio
async def test_scanner_with_default_config():
    scanner = Scanner(root_path=TEST_REPO, exclude_dirs=EXCLUDED_DIRS_DEFAULT, verbose=True, use_ignore_file=True, size_limit=5 * 1024 * 1024)
    included = await scanner.scan_directory()

    print("INCLUDED FILES:", [str(f) for f in included])

    assert isinstance(included, list)
    assert any("script.py" in str(f) for f in included), "Expected script.py not found"
    assert all("node_modules" not in str(f) for f in included), "Should exclude node_modules"
    assert all(not f.name.endswith(".zip") for f in included), "ZIP files should be excluded"
    assert all("script_large.py" not in str(f) for f in included), "Large files should be skipped"

@pytest.mark.asyncio
async def test_scanner_skipped_reasons():
    scanner = Scanner(root_path=TEST_REPO, exclude_dirs=EXCLUDED_DIRS_DEFAULT, verbose=True, use_ignore_file=True, size_limit=5 * 1024 * 1024)
    _ = await scanner.scan_directory()
    skipped = scanner.skipped_files

    print("SKIPPED FILES:", skipped)

    assert any("script_large.py" in str(p) for p, _ in skipped), "Expected script_large.py to be skipped"
    assert any("binary.dat" in str(p) for p, _ in skipped), "Expected binary.dat to be skipped"
    assert any("archive.zip" in str(p) for p, _ in skipped), "Expected archive.zip to be skipped"

@pytest.mark.asyncio
async def test_scanner_with_include_pattern():
    scanner = Scanner(root_path=TEST_REPO, exclude_dirs=EXCLUDED_DIRS_DEFAULT, include_patterns=["*.txt"], verbose=True)
    included = await scanner.scan_directory()

    print("INCLUDED FILES:", [str(f) for f in included])

    assert any("included.txt" in str(f) for f in included), "Expected included.txt to be found"
    assert all(f.name.endswith(".txt") for f in included), "Only .txt files should be included"

@pytest.mark.asyncio
async def test_scanner_with_exclude_pattern():
    scanner = Scanner(root_path=TEST_REPO, exclude_dirs=EXCLUDED_DIRS_DEFAULT, exclude_patterns=["*.csv", "*.min.js"], verbose=True)
    included = await scanner.scan_directory()

    print("INCLUDED FILES:", [str(f) for f in included])

    assert all(
        not f.name.endswith(".csv") and not f.name.endswith(".min.js")
        for f in included
    ), "CSV and min.js files should be excluded"
