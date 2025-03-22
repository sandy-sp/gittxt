import os
import shutil

def test_cli_tree(cli_runner, test_repo):
    result = cli_runner.invoke("cli", ["tree", str(test_repo)])
    assert result.exit_code == 0
    assert "src" in result.output
    assert "docs" in result.output

def test_cli_classify(cli_runner, test_repo):
    py_file = test_repo / "src" / "example.py"
    result = cli_runner.invoke("cli", ["classify", str(py_file)])
    assert result.exit_code == 0
    assert "code" in result.output

def test_cli_clean(cli_runner, tmp_path):
    out_dir = tmp_path / "gittxt-out"
    (out_dir / "text").mkdir(parents=True)
    (out_dir / "text" / "dummy.txt").write_text("data")
    result = cli_runner.invoke("cli", ["clean", "--output-dir", str(out_dir)])
    assert result.exit_code == 0
    assert not (out_dir / "text").exists()

def test_cli_scan(tmp_path, cli_runner, test_repo):
    out_dir = tmp_path / "gittxt-output"
    result = cli_runner.invoke(
        "cli",
        [
            "scan", str(test_repo),
            "--output-dir", str(out_dir),
            "--file-types", "code,docs,csv",
            "--output-format", "txt,json,md",
            "--non-interactive",
            "--zip",
            "--summary"
        ]
    )
    assert result.exit_code == 0
    assert "Summary Report" in result.output
    assert (out_dir / "text").exists()
    assert (out_dir / "json").exists()
    assert (out_dir / "md").exists()
    assert (out_dir / "zips").exists()

def test_cli_tree_depth(cli_runner, test_repo):
    # Ensure tree with depth limitation works
    result = cli_runner.invoke("cli", ["tree", str(test_repo), "--tree-depth", "1"])
    assert result.exit_code == 0
    assert "src" in result.output
    assert "level2" not in result.output  # deeper than level 1


def test_cli_scan_noninteractive_zip(cli_runner, tmp_path, test_repo):
    out_dir = tmp_path / "cli-out"
    result = cli_runner.invoke(
        "cli",
        [
            "scan", str(test_repo),
            "--output-dir", str(out_dir),
            "--file-types", "code,docs",
            "--output-format", "txt,json",
            "--non-interactive",
            "--zip"
        ]
    )
    assert result.exit_code == 0
    assert (out_dir / "zips").exists()
    assert any(".zip" in str(p) for p in (out_dir / "zips").glob("*.zip"))
