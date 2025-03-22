from gittxt.utils import pattern_utils

def test_include_and_exclude_matching(tmp_path):
    repo_root = tmp_path
    file = repo_root / "src" / "main.py"
    file.parent.mkdir(parents=True)
    file.write_text("print('ok')")

    include_patterns = ["*.py"]
    exclude_patterns = ["src/*"]

    assert pattern_utils.match_include(file, include_patterns, root=repo_root) is True
    assert pattern_utils.match_exclude(file, exclude_patterns, root=repo_root) is True


def test_normalize_patterns():
    patterns = [" *.PY ", "*.Md", " .git "]
    normalized = pattern_utils.normalize_patterns(patterns)
    assert normalized == ["*.py", "*.md", ".git"]


def test_passes_all_filters(tmp_path):
    py_file = tmp_path / "script.py"
    md_file = tmp_path / "README.md"
    py_file.write_text("print('ok')")
    md_file.write_text("# header")

    # 1. Should pass: includes python file, no excludes
    assert pattern_utils.passes_all_filters(py_file, ["*.py"], [], size_limit=100)

    # 2. Should fail: excluded by pattern
    assert pattern_utils.passes_all_filters(md_file, [], ["*.md"], size_limit=100) is False

    # 3. Should fail: size exceeds limit
    big_file = tmp_path / "large.txt"
    big_file.write_text("X" * 1024)
    assert pattern_utils.passes_all_filters(big_file, [], [], size_limit=100) is False
