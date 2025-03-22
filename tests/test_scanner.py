from gittxt.scanner import Scanner

def test_scanner_basic_functionality(tmp_path):
    # Setup mock repo with test files
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "assets").mkdir()

    (tmp_path / "README.md").write_text("# Readme")
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "docs" / "guide.md").write_text("## Guide")
    (tmp_path / "assets" / "image.png").write_bytes(b"FAKEPNGDATA")

    # TEXTUAL scan (default)
    scanner = Scanner(
        root_path=tmp_path,
        include_patterns=[],
        exclude_patterns=["assets/*"],
        size_limit=None,
        file_types=["code", "docs"],
        progress=False,
    )

    files, _ = scanner.scan_directory()
    file_names = [f.name for f in files]

    assert "README.md" in file_names
    assert "main.py" in file_names
    assert "guide.md" in file_names
    assert "image.png" not in file_names


def test_scanner_respects_size_limit(tmp_path):
    large_file = tmp_path / "large_file.txt"
    small_file = tmp_path / "small_file.txt"

    large_file.write_text("X" * 1024 * 1024)  # ~1MB
    small_file.write_text("OK")

    scanner = Scanner(
        root_path=tmp_path,
        include_patterns=[],
        exclude_patterns=[],
        size_limit=100,  # 100 bytes
        file_types=["docs"],
        progress=False,
    )

    files, _ = scanner.scan_directory()
    file_names = [f.name for f in files]

    assert "small_file.txt" in file_names
    assert "large_file.txt" not in file_names


def test_scanner_include_exclude(tmp_path):
    # Create deep structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ignore_me.py").write_text("print('no')")
    (tmp_path / "src" / "keep_me.py").write_text("print('yes')")

    scanner = Scanner(
        root_path=tmp_path,
        include_patterns=["*keep_me.py"],
        exclude_patterns=["*ignore_me.py"],
        size_limit=None,
        file_types=["code"],
        progress=False,
    )

    files, _ = scanner.scan_directory()
    file_names = [f.name for f in files]

    assert "keep_me.py" in file_names
    assert "ignore_me.py" not in file_names
