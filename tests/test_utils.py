# tests/test_utils.py

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
    assert filetype_utils.classify_file(py_file) == "text"

    bin_file = tmp_path / "file.bin"
    bin_file.write_bytes(b"\x00\x01\x02")
    assert filetype_utils.classify_file(bin_file) == "asset"

def test_fallback_on_text_content(tmp_path):
    unknown = tmp_path / "file.unknown"
    unknown.write_text("def main(): pass")
    assert filetype_utils.classify_file(unknown) == "text"

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
def test_generate_summary(tmp_path):
    file1 = tmp_path / "a.py"
    file1.write_text("print('hello')")

    file2 = tmp_path / "b.txt"
    file2.write_text("some text data")

    summary = summary_utils.generate_summary([file1, file2])
    assert summary["total_files"] == 2
    assert summary["text_files"] >= 1
    assert summary["total_size"] > 0
    assert summary["estimated_tokens"] > 0

# -------- pattern_utils tests --------
def test_include_exclude_patterns(tmp_path):
    file = tmp_path / "sample.py"
    file.write_text("print('ok')")

    assert pattern_utils.match_include(file, [".py"]) is True
    assert pattern_utils.match_exclude(file, ["node_modules", "sample"]) is True
    assert pattern_utils.match_exclude(file, ["dist"]) is False

def test_normalize_patterns():
    raw_patterns = [" .git ", " __pycache__ "]
    result = pattern_utils.normalize_patterns(raw_patterns)
    assert result == [".git", "__pycache__"]
