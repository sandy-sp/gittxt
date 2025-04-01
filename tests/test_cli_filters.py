import pytest
from click.testing import CliRunner
from gittxt.cli.cli_filters import filters
from gittxt.core.config import ConfigManager


@pytest.fixture(autouse=True)
def reset_filters():
    # Reset all filters before each test
    ConfigManager.update_filter_list("textual_exts", [])
    ConfigManager.update_filter_list("non_textual_exts", [])
    ConfigManager.update_filter_list("excluded_dirs", [])
    yield
    # Reset after each test as well
    ConfigManager.update_filter_list("textual_exts", [])
    ConfigManager.update_filter_list("non_textual_exts", [])
    ConfigManager.update_filter_list("excluded_dirs", [])


def test_list_filters_empty():
    runner = CliRunner()
    result = runner.invoke(filters, ["list"])
    assert result.exit_code == 0
    assert "Textual Extensions" in result.output
    assert "Excluded Directories" in result.output


def test_add_textual_filter_removes_from_non_textual():
    runner = CliRunner()
    # Add to non-textual first
    runner.invoke(filters, ["add", "non_textual_exts", ".py"])
    # Now add to textual, which should remove it from non-textual
    runner.invoke(filters, ["add", "textual_exts", ".py"])

    config = ConfigManager.load_config()
    assert ".py" in config["filters"]["textual_exts"]
    assert ".py" not in config["filters"]["non_textual_exts"]


def test_add_non_textual_blocked_if_in_textual():
    runner = CliRunner()
    runner.invoke(filters, ["add", "textual_exts", ".csv"])
    result = runner.invoke(filters, ["add", "non_textual_exts", ".csv"])
    assert "Cannot move from textual to non-textual" in result.output


def test_add_and_remove_excluded_dirs():
    runner = CliRunner()
    runner.invoke(filters, ["add", "excluded_dirs", ".git", "dist"])
    config = ConfigManager.load_config()
    assert ".git" in config["filters"]["excluded_dirs"]
    assert "dist" in config["filters"]["excluded_dirs"]

    runner.invoke(filters, ["remove", "excluded_dirs", "dist"])
    config = ConfigManager.load_config()
    assert "dist" not in config["filters"]["excluded_dirs"]
    assert ".git" in config["filters"]["excluded_dirs"]


def test_clear_filters():
    runner = CliRunner()
    runner.invoke(filters, ["add", "textual_exts", ".html"])
    runner.invoke(filters, ["add", "excluded_dirs", ".venv"])
    result = runner.invoke(filters, ["clear"])

    config = ConfigManager.load_config()
    for key in ["textual_exts", "non_textual_exts", "excluded_dirs"]:
        assert config["filters"].get(key) == []
