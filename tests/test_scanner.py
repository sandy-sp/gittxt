import pytest
from pathlib import Path
from gittxt.scanner import Scanner

@pytest.fixture
def dummy_repo(tmp_path):
    # Setup a dummy repo with mixed files
    repo = tmp_path / "dummy-repo"
    repo.mkdir()

    (repo / "app.py").write_text("print('hello')")  # code
    (repo / "README.md").write_text("# Docs")      # docs
    (repo / "data.csv").write_text("id,value\n1,100")  # csv
    (repo / "logo.png").write_bytes(b"\x89PNG\r\n")    # binary
    (repo / "large.bin").write_bytes(b"A" * 2_000_000) # large file
    (repo / "notes.txt").write_text("Some text")   # text
    (repo / "nested").mkdir()
    (repo / "nested" / "deepfile.py").write_text("# deep code file")

    return repo

def test_include_pattern_py(dummy_repo):
    scanner = Scanner(
        root_path=dummy_repo,
        include_patterns=[".py"],
        exclude_patterns=[],
        size_limit=None,
        file_types=["all"],
    )
    files, _ = scanner.scan_directory()
    assert all(str(f).endswith(".py") for f in files)
    assert any("app.py" in str(f) for f in files)

def test_exclude_nested_folder(dummy_repo):
    scanner = Scanner(
        root_path=dummy_repo,
        include_patterns=[],
        exclude_patterns=["nested"],
        size_limit=None,
        file_types=["all"],
    )
    files, _ = scanner.scan_directory()
    assert not any("nested" in str(f) for f in files)

def test_filetype_docs_only(dummy_repo):
    scanner = Scanner(
        root_path=dummy_repo,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=None,
        file_types=["docs"],
    )
    files, _ = scanner.scan_directory()
    assert any("README.md" in str(f) for f in files)
    assert all(f.suffix in [".md", ".rst", ".txt"] for f in files)

def test_size_limit_excludes_large_file(dummy_repo):
    scanner = Scanner(
        root_path=dummy_repo,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=500_000,  # 500 KB
        file_types=["all"],
    )
    files, _ = scanner.scan_directory()
    assert not any("large.bin" in str(f) for f in files)

def test_filetype_csv(dummy_repo):
    scanner = Scanner(
        root_path=dummy_repo,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=None,
        file_types=["csv"],
    )
    files, _ = scanner.scan_directory()
    assert any("data.csv" in str(f) for f in files)

def test_all_files_included(dummy_repo):
    scanner = Scanner(
        root_path=dummy_repo,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=None,
        file_types=["all"],
    )
    files, _ = scanner.scan_directory()
    assert len(files) >= 6  # Expecting at least all dummy files to be counted

