import click
import pytest
from click.testing import CliRunner
from gittxt.cli import cli

def test_invalid_filetypes_flag(cli_runner: CliRunner, test_repo):
    result = cli_runner.invoke("cli", ["scan", str(test_repo), "--file-types", "codex"])
    assert result.exit_code != 0
    assert "Invalid file type" in result.output


def test_cli_missing_repo(cli_runner: CliRunner):
    result = cli_runner.invoke("cli", ["scan"])
    assert result.exit_code != 0
    assert "No repositories specified" in result.output


def test_interactive_whitelist_prompt(monkeypatch, cli_runner: CliRunner, tmp_path):
    # Inject a dummy unknown extension file
    custom_file = tmp_path / "unknown.customext"
    custom_file.write_text("dummy content")

    # Patch click.confirm to simulate user adding to whitelist
    monkeypatch.setattr(click, "confirm", lambda *args, **kwargs: True)

    result = cli_runner.invoke(
        "cli",
        [
            "scan", str(tmp_path),
            "--file-types", "all",
            "--non-interactive", "False"
        ]
    )
    # We just want to ensure no crash and that whitelist confirmation works
    assert result.exit_code == 0
