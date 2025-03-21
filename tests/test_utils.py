import pytest
from pathlib import Path
from gittxt.utils import repo_url_parser, filetype_utils, summary_utils, pattern_utils

# -------- repo_url_parser tests --------
def test_parse_https_url():
    url = "https://github.com/user/repo.git"
    result = repo_url_parser.parse_github_url(url)
    assert result["owner"] == "user"
    assert result["repo"] == "repo"
    assert result["branch"] == "main"

def test_parse_ssh_url():
    url = "git@github.com:user/repo.git"
    result = repo_url_parser.parse_github_url(url)
    assert result["owner"] == "user"
    assert result["repo"] == "repo"

def test_parse_with_subdir_and_branch():
    url = "https://github.com/user/repo/tree/dev/src/"
    result = repo_url_parser.parse_github_url(url)
    assert result["branch"] == "dev"
    assert result["subdir"] == "src"

def test_invalid_url():
    with pytest.raises(ValueError):
        repo_url_parser.parse_github_url("https://gitlab.com/user/repo")

# -------- filetype_utils tests --------
def test_classify_known_extensions(tmp_path):
    py_file = tmp_path / "test.py"
    py_file.write_text("print('hello')")
    assert filetype_utils.classify_file(py_file) == "code"

    md_file = tmp_path / "readme.md"
    md_file.write_text("# Docs")
    assert filetype_utils.classify_file(md_file) == "docs"

    csv_file = tmp_path / "data.csv"
    csv_file.write_text("col1,col2")
    assert filetype_utils.classify_file(csv_file) == "csv"

def test_fallback_on_text_content(tmp_path):
    unknown = tmp_path / "file.unknown"
    unknown.write_text("def main(): pass")
    assert filetype_utils.classify_file(unknown) in {"code", "docs"}

def test_whitelist_and_blacklist(tmp_path):
    dummy = tmp_path / "foo.customext"
    dummy.write_text("custom text")

    # Simulate adding .customext to whitelist
    filetype_utils.update_whitelist(".customext")
    assert filetype_utils.is_whitelisted(dummy)

    filetype_utils.update_blacklist(".blocked")
    blocked = tmp_path / "file.blocked"
    blocked.write_text("data")
    assert filetype_utils.is_blacklisted(blocked)

# -------- summary_utils tests --------
def test_generate_summary_and_tokens_by_type(tmp_path):
    py_file = tmp_path / "app.py"
    py_file.write_text("print('hello')")

    md_file = tmp_path / "readme.md"
    md_file.write_text("# Docs section")

    csv_file = tmp_path / "data.csv"
    csv_file.write_text("id,value\n1,100")

    files = [py_file, md_file, csv_file]
    summary = summary_utils.generate_summary(files)

    assert summary["total_files"] == 3
    assert summary["total_size"] > 0
    assert summary["estimated_tokens"] > 0

    assert "code" in summary["tokens_by_type"]
    assert "docs" in summary["tokens_by_type"]
    assert "csv" in summary["tokens_by_type"]

    assert summary["tokens_by_type"]["code"] > 0
    assert summary["tokens_by_type"]["docs"] > 0
    assert summary["tokens_by_type"]["csv"] > 0

# -------- pattern_utils tests --------
def test_include_exclude_patterns(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("print('ok')")

    assert pattern_utils.match_include(file, ["*.py"]) is True
    assert pattern_utils.match_exclude(file, ["*/sample.py"]) is True
    assert pattern_utils.match_exclude(file, ["dist"]) is False

def test_normalize_patterns():
    raw_patterns = [" .git ", " __pycache__ "]
    result = pattern_utils.normalize_patterns(raw_patterns)
    assert result == [".git", "__pycache__"]
