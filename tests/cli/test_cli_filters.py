import pytest
from click.testing import CliRunner
from gittxt.cli.cli_config import config
from gittxt.core.config import ConfigManager


@pytest.fixture(autouse=True)
def reset_filters():
    # Reset all filters before and after each test
    for key in ["textual_exts", "non_textual_exts", "excluded_dirs"]:
        ConfigManager.update_filter_list(key, [])
    yield
    for key in ["textual_exts", "non_textual_exts", "excluded_dirs"]:
        ConfigManager.update_filter_list(key, [])


def test_list_filters_empty():
    runner = CliRunner()
    result = runner.invoke(config, ["filters", "list"])
    assert result.exit_code == 0
    assert "Textual Extensions" in result.output
    assert "Excluded Directories" in result.output


def test_add_textual_filter_removes_from_non_textual():
    runner = CliRunner()
    runner.invoke(config, ["filters", "add", "non_textual_exts", ".py"])
    runner.invoke(config, ["filters", "add", "textual_exts", ".py"])

    config_data = ConfigManager.load_config()
    assert ".py" in config_data["filters"]["textual_exts"]
    assert ".py" not in config_data["filters"]["non_textual_exts"]


def test_add_non_textual_blocked_if_in_textual():
    runner = CliRunner()
    runner.invoke(config, ["filters", "add", "textual_exts", ".csv"])
    result = runner.invoke(config, ["filters", "add", "non_textual_exts", ".csv"])
    assert "Cannot move from textual to non-textual" in result.output


def test_add_and_remove_excluded_dirs():
    runner = CliRunner()
    runner.invoke(config, ["filters", "add", "excluded_dirs", ".git", "dist"])
    config_data = ConfigManager.load_config()
    assert ".git" in config_data["filters"]["excluded_dirs"]
    assert "dist" in config_data["filters"]["excluded_dirs"]

    runner.invoke(config, ["filters", "remove", "excluded_dirs", "dist"])
    config_data = ConfigManager.load_config()
    assert "dist" not in config_data["filters"]["excluded_dirs"]
    assert ".git" in config_data["filters"]["excluded_dirs"]


def test_clear_filters():
    runner = CliRunner()
    runner.invoke(config, ["filters", "add", "textual_exts", ".html"])
    runner.invoke(config, ["filters", "add", "excluded_dirs", ".venv"])
    runner.invoke(config, ["filters", "clear"])

    config_data = ConfigManager.load_config()
    for key in ["textual_exts", "non_textual_exts", "excluded_dirs"]:
        assert config_data["filters"].get(key) == []
