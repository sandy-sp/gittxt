import subprocess
import os

def test_cli_help():
    """Test if CLI help runs correctly."""
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"  # Ensure PYTHONPATH is set for subprocess

    result = subprocess.run(
        ["python", "src/gittxt/cli.py", "--help"], 
        capture_output=True, text=True, env=env
    )

    assert "Usage:" in result.stdout

def test_cli_scan_local(tmp_path):
    """Test CLI scanning a local directory."""
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    (test_dir / "file.py").write_text("print('Hello')")

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"  # Ensure PYTHONPATH is set for subprocess

    result = subprocess.run(
        ["python", "src/gittxt/cli.py", str(test_dir)],
        capture_output=True, text=True, env=env
    )

    print("\n--- DEBUG: CLI OUTPUT ---")
    print(result.stdout)
    print("--- END DEBUG ---\n")

    assert "Found 1 valid files" in result.stdout

def test_cli_scan_local(tmp_path):
    """Test CLI scanning a local directory."""
    test_dir = tmp_path / "test_project"
    test_dir.mkdir()
    (test_dir / "file.py").write_text("print('Hello')")

    env = os.environ.copy()
    env["PYTHONPATH"] = "src"  # Ensure PYTHONPATH is set for subprocess

    result = subprocess.run(
        ["python", "src/gittxt/cli.py", str(test_dir)],
        capture_output=True, text=True, env=env
    )

    print("\n--- DEBUG: CLI OUTPUT ---")
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)
    print("--- END DEBUG ---\n")

    assert "Found 1 valid files" in result.stdout
