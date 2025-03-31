import pytest
import os
from pathlib import Path
from gittxt.core.scanner import Scanner
from gittxt.core.constants import EXCLUDED_DIRS_DEFAULT

TEST_REPO = Path("tests/test_repo")


@pytest.mark.asyncio
async def test_scanner_with_default_config():
    scanner = Scanner(
        root_path=TEST_REPO,
        exclude_dirs=EXCLUDED_DIRS_DEFAULT,
        verbose=True,
        use_ignore_file=True,
        size_limit=5 * 1024 * 1024,
    )
    included = await scanner.scan_directory()

    print("INCLUDED FILES:", [str(f) for f in included])

    assert isinstance(included, list)
    assert any("script.py" in str(f) for f in included), "Expected script.py not found"
    assert all(
        "node_modules" not in str(f) for f in included
    ), "Should exclude node_modules"
    assert all(
        not f.name.endswith(".zip") for f in included
    ), "ZIP files should be excluded"
    assert all(
        "script_large.py" not in str(f) for f in included
    ), "Large files should be skipped"


@pytest.mark.asyncio
async def test_scanner_skipped_reasons():
    scanner = Scanner(
        root_path=TEST_REPO,
        exclude_dirs=EXCLUDED_DIRS_DEFAULT,
        verbose=True,
        use_ignore_file=True,
        size_limit=5 * 1024 * 1024,
    )
    _ = await scanner.scan_directory()
    skipped = scanner.skipped_files

    print("SKIPPED FILES:", skipped)

    assert any(
        "script_large.py" in str(p) for p, _ in skipped
    ), "Expected script_large.py to be skipped"
    assert any(
        "binary.dat" in str(p) for p, _ in skipped
    ), "Expected binary.dat to be skipped"
    assert any(
        "archive.zip" in str(p) for p, _ in skipped
    ), "Expected archive.zip to be skipped"


@pytest.mark.asyncio
async def test_scanner_with_include_pattern():
    scanner = Scanner(
        root_path=TEST_REPO,
        exclude_dirs=EXCLUDED_DIRS_DEFAULT,
        include_patterns=["*.txt"],
        verbose=True,
    )
    included = await scanner.scan_directory()

    print("INCLUDED FILES:", [str(f) for f in included])

    assert any(
        "included.txt" in str(f) for f in included
    ), "Expected included.txt to be found"
    assert all(
        f.name.endswith(".txt") for f in included
    ), "Only .txt files should be included"


@pytest.mark.asyncio
async def test_scanner_with_exclude_pattern():
    scanner = Scanner(
        root_path=TEST_REPO,
        exclude_dirs=EXCLUDED_DIRS_DEFAULT,
        exclude_patterns=["*.csv", "*.min.js"],
        verbose=True,
    )
    included = await scanner.scan_directory()

    print("INCLUDED FILES:", [str(f) for f in included])

    assert all(
        not f.name.endswith(".csv") and not f.name.endswith(".min.js") for f in included
    ), "CSV and min.js files should be excluded"

@pytest.mark.asyncio
async def test_scanner_respects_gittxtignore(tmp_path):
    # Setup test repo
    test_dir = tmp_path / "repo"
    test_dir.mkdir()
    (test_dir / "keep.txt").write_text("This should be kept")
    (test_dir / "skip.zip").write_text("Binary content")
    (test_dir / "node_modules").mkdir()
    (test_dir / "node_modules" / "lib.js").write_text("console.log('test')")

    # Create .gittxtignore
    (test_dir / ".gittxtignore").write_text("*.zip\nnode_modules/")

    scanner = Scanner(
        root_path=test_dir,
        use_ignore_file=True,
        progress=False,
    )
    accepted, non_textual = await scanner.scan_directory()

    accepted_names = [p.name for p in accepted]
    assert "keep.txt" in accepted_names
    assert "skip.zip" not in accepted_names
    assert all("node_modules" not in str(p) for p in accepted)

@pytest.mark.asyncio
async def test_scanner_with_no_size_limit(tmp_path):
    test_dir = tmp_path / "repo"
    test_dir.mkdir()
    large_file = test_dir / "big.txt"
    large_file.write_text("x" * 10_000_000)  # ~10MB

    scanner = Scanner(
        root_path=test_dir,
        size_limit=None,
        progress=False,
    )
    accepted, _ = await scanner.scan_directory()
    assert large_file in accepted

@pytest.mark.asyncio
async def test_scanner_skips_on_processing_error(tmp_path):
    test_dir = tmp_path / "repo"
    test_dir.mkdir()

    # Create a fake file and remove read permission to trigger an error
    broken_file = test_dir / "corrupt.txt"
    broken_file.write_text("trigger error")
    os.chmod(broken_file, 0)  # remove all permissions

    scanner = Scanner(
        root_path=test_dir,
        progress=False,
    )
    accepted, _ = await scanner.scan_directory()

    # Restore permission so test teardown doesn't fail
    os.chmod(broken_file, 0o644)

    # The file should be skipped
    assert broken_file not in accepted

    skipped_paths = [p for p, _ in scanner.skipped_files]
    assert broken_file.resolve() in [p.resolve() for p in skipped_paths]
