import click
from click.testing import CliRunner
from gittxt.cli import cli

def test_scan_command(tmp_path, test_repo):
    runner = CliRunner()
    out_dir = tmp_path / "gittxt-output"
    result = runner.invoke(cli, [
        "scan", str(test_repo),
        "--output-dir", str(out_dir),
        "--file-types", "code,docs",
        "--output-format", "txt,json",
        "--non-interactive",
        "--zip",
        "--summary"
    ])
    assert result.exit_code == 0
    assert (out_dir / "text").exists()
    assert (out_dir / "json").exists()
    assert (out_dir / "zips").exists()
    assert "Summary Report" in result.output


def test_tree_command(test_repo):
    runner = CliRunner()
    result = runner.invoke(cli, ["tree", str(test_repo)])
    assert result.exit_code == 0
    assert "src" in result.output


def test_classify_command(test_repo):
    runner = CliRunner()
    py_file = test_repo / "src" / "example.py"
    result = runner.invoke(cli, ["classify", str(py_file)])
    assert result.exit_code == 0
    assert "code" in result.output


def test_clean_command(tmp_path):
    runner = CliRunner()
    out_dir = tmp_path / "clean-output"
    (out_dir / "text").mkdir(parents=True)
    (out_dir / "text" / "dummy.txt").write_text("dummy")
    result = runner.invoke(cli, ["clean", "--output-dir", str(out_dir)])
    assert result.exit_code == 0
    assert not (out_dir / "text").exists()


def test_whitelist_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["whitelist", ".customext"])
    assert result.exit_code == 0
    assert "Added" in result.output


def test_blacklist_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["blacklist", ".bak"])
    assert result.exit_code == 0
    assert "Added" in result.output


def test_interactive_whitelist_prompt(monkeypatch, cli_runner: CliRunner, tmp_path):
    custom_file = tmp_path / "unknown.customext"
    custom_file.write_text("dummy content")

    monkeypatch.setattr(click, "confirm", lambda *args, **kwargs: True)

    result = cli_runner.invoke(cli, [
        "scan", str(tmp_path),
        "--file-types", "all"
    ])
    assert result.exit_code == 0
