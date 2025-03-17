import pytest
from gittxt.utils.repo_url_parser import parse_github_url


def test_main_repo_url():
    url = "https://github.com/sandy-sp/gittxt.git"
    result = parse_github_url(url)
    assert result["owner"] == "sandy-sp"
    assert result["repo"] == "gittxt"
    assert result["branch"] == "main"
    assert result["subdir"] is None or result["subdir"] == ""


def test_with_branch_dev():
    url = "https://github.com/sandy-sp/gittxt/tree/UI-Dev"
    result = parse_github_url(url)
    assert result["branch"] == "UI-Dev"
    assert result["subdir"] is None or result["subdir"] == ""


def test_with_branch_and_subdir():
    url = "https://github.com/sandy-sp/gittxt/tree/ui-dev-2/src/gittxt_ui"
    result = parse_github_url(url)
    assert result["branch"] == "ui-dev-2"
    assert result["subdir"] == "src/gittxt_ui"


def test_ssh_url():
    url = "git@github.com:sandy-sp/gittxt.git"
    result = parse_github_url(url)
    assert result["owner"] == "sandy-sp"
    assert result["repo"] == "gittxt"
    assert result["branch"] is None
    assert result["subdir"] is None


def test_invalid_url():
    with pytest.raises(ValueError):
        parse_github_url("https://gitlab.com/sandy-sp/gittxt")


def test_missing_repo_name():
    with pytest.raises(ValueError):
        parse_github_url("https://github.com/sandy-sp/")
