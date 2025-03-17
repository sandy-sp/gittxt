import pytest
from pathlib import Path
from gittxt.scanner import Scanner

@pytest.fixture
def mock_repo(tmp_path):
    repo_path = tmp_path / "test-repo"
    repo_path.mkdir()
    (repo_path / "app.py").write_text("print('Test')")
    (repo_path / "README.md").write_text("# Sample Doc")
    (repo_path / "assets").mkdir()
    (repo_path / "assets/data.csv").write_text("id,value\n1,100")
    (repo_path / "assets/logo.png").write_bytes(b"\x89PNG\r\n")
    (repo_path / "big.txt").write_text("A" * 1_000_000)  # Large file
    return repo_path

def test_includes_code_only(mock_repo):
    scanner = Scanner(
        root_path=mock_repo,
        include_patterns=[".py"],
        exclude_patterns=[],
        size_limit=None,
        file_types=["code"]
    )
    files, _ = scanner.scan_directory()
    assert any("app.py" in str(f) for f in files)
    assert all(str(f).endswith(".py") for f in files)

def test_excludes_assets_folder(mock_repo):
    scanner = Scanner(
        root_path=mock_repo,
        include_patterns=[],
        exclude_patterns=["assets"],
        size_limit=None,
        file_types=["all"]
    )
    files, _ = scanner.scan_directory()
    assert not any("data.csv" in f or "logo.png" in f for f in files)

def test_filetype_docs_only(mock_repo):
    scanner = Scanner(
        root_path=mock_repo,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=None,
        file_types=["docs"]
    )
    files, _ = scanner.scan_directory()
    
    assert any("README" in Path(f).name for f in files)

    # Accept common doc extensions
    allowed = [".md", ".rst", ".txt"]
    assert all(Path(f).suffix in allowed or "README" in Path(f).name for f in files)

def test_filetype_csv(mock_repo):
    scanner = Scanner(
        root_path=mock_repo,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=None,
        file_types=["csv"]
    )
    files, _ = scanner.scan_directory()
    assert any("data.csv" in str(f) for f in files)

def test_image_files_filtered(mock_repo):
    scanner = Scanner(
        root_path=mock_repo,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=None,
        file_types=["image"]
    )
    files, _ = scanner.scan_directory()
    assert any("logo.png" in str(f) for f in files)

def test_size_limit(mock_repo):
    scanner = Scanner(
        root_path=mock_repo,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=1000,  # 1 KB
        file_types=["all"]
    )
    files, _ = scanner.scan_directory()
    assert not any("big.txt" in str(f) for f in files)
