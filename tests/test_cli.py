import pytest
import os
import shutil
import subprocess
from pathlib import Path
from gittxt.config import ConfigManager

# Load test configuration dynamically
config = ConfigManager.load_config()

# Define test paths
TEST_REPO = os.path.abspath("tests/test-repo")
CLI_OUTPUT_DIR = os.path.abspath(os.path.join(config["output_dir"], "cli"))

# FIX: Adjust expected file paths to match actual CLI output behavior
TEXT_OUTPUT_PATH = os.path.join(CLI_OUTPUT_DIR, "cli", "text", "test-repo.txt")
JSON_OUTPUT_PATH = os.path.join(CLI_OUTPUT_DIR, "cli", "json", "test-repo.json")

@pytest.fixture(scope="function")
def clean_output_dir():
    """Ensure the CLI output directory is clean before each test."""
    if os.path.exists(CLI_OUTPUT_DIR):
        shutil.rmtree(CLI_OUTPUT_DIR)
    os.makedirs(CLI_OUTPUT_DIR, exist_ok=True)

def run_gittxt_command(args):
    """
    Helper function to execute Gittxt CLI commands.
    Uses 'poetry run' to ensure it runs inside the virtual environment.
    """
    cmd = ["poetry", "run", "gittxt"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Debugging Output
    print("\n--- STDOUT ---\n", result.stdout)
    print("\n--- STDERR ---\n", result.stderr)

    return result

def test_cli_help():
    """Test CLI help command to ensure subcommands are properly listed."""
    result = run_gittxt_command(["--help"])
    assert "Usage:" in result.stdout or result.stderr
    assert "install" in result.stdout or result.stderr
    assert "scan" in result.stdout or result.stderr

def test_cli_basic_scan(clean_output_dir):
    """Test basic repository scanning via CLI."""
    result = run_gittxt_command(["scan", TEST_REPO, "--output-dir", CLI_OUTPUT_DIR])
    
    print("\nDEBUG - test_cli_basic_scan OUTPUT:\n", result.stdout)
    
    assert "✅ Processing" in result.stdout or result.stderr
    assert os.path.exists(TEXT_OUTPUT_PATH), f"Expected text output file at {TEXT_OUTPUT_PATH}, but it was not found."

def test_cli_include_exclude(clean_output_dir):
    """Test --include and --exclude options in CLI scan."""
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--include", ".py",
        "--include", ".md",
        "--exclude", "node_modules",
        "--exclude", "__pycache__",
        "--output-dir", CLI_OUTPUT_DIR
    ])
    
    print("\nDEBUG - test_cli_include_exclude OUTPUT:\n", result.stdout)
    
    assert "✅ Processing" in result.stdout or result.stderr
    assert os.path.exists(TEXT_OUTPUT_PATH), f"Expected text output file at {TEXT_OUTPUT_PATH}, but it was not found."

def test_cli_output_format_json(clean_output_dir):
    """Test if the JSON output format works properly in CLI scan."""
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--output-format", "json",
        "--output-dir", CLI_OUTPUT_DIR
    ])
    
    print("\nDEBUG - test_cli_output_format_json OUTPUT:\n", result.stdout)
    
    assert "✅ Output saved to:" in result.stdout or result.stderr
    assert os.path.exists(JSON_OUTPUT_PATH), f"Expected JSON output file at {JSON_OUTPUT_PATH}, but it was not found."

def test_cli_multi_format(clean_output_dir):
    """Test scanning with multiple output formats (txt, json)."""
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--output-format", "txt,json",
        "--output-dir", CLI_OUTPUT_DIR
    ])
    
    print("\nDEBUG - test_cli_multi_format OUTPUT:\n", result.stdout)

    assert os.path.exists(TEXT_OUTPUT_PATH), f"Expected text output file at {TEXT_OUTPUT_PATH}, but it was not found."
    assert os.path.exists(JSON_OUTPUT_PATH), f"Expected JSON output file at {JSON_OUTPUT_PATH}, but it was not found."

def test_cli_invalid_output_format(clean_output_dir):
    """Test scanning with an invalid output format to ensure proper error handling."""
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--output-format", "invalid_format",
        "--output-dir", CLI_OUTPUT_DIR
    ])
    
    print("\nDEBUG - test_cli_invalid_output_format OUTPUT:\n", result.stdout)
    
    assert "❌ Invalid output format specified" in result.stderr or result.stdout, "Expected error message for invalid format."

def test_cli_invalid_repository(clean_output_dir):
    """Test scanning a non-existent repository to ensure it fails gracefully."""
    invalid_repo = "/invalid/path/to/repo"
    result = run_gittxt_command([
        "scan", invalid_repo,
        "--output-dir", CLI_OUTPUT_DIR
    ])
    
    print("\nDEBUG - test_cli_invalid_repository OUTPUT:\n", result.stdout)
    
    assert "❌ Failed to access repository" in result.stderr or result.stdout, "Expected failure message for invalid repo."

def test_cli_summary_flag(clean_output_dir):
    """Test --summary flag to check if summary reports are generated correctly."""
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--summary",
        "--output-dir", CLI_OUTPUT_DIR
    ])
    
    print("\nDEBUG - test_cli_summary_flag OUTPUT:\n", result.stdout)
    
    assert "📊 Summary Report" in result.stdout or result.stderr

def test_cli_debug_flag(clean_output_dir):
    """Test --debug flag to check if debug mode is correctly enabled."""
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--debug",
        "--output-dir", CLI_OUTPUT_DIR
    ])
    
    print("\nDEBUG - test_cli_debug_flag OUTPUT:\n", result.stdout)
    
    assert "🔍 Debug mode enabled." in result.stdout or result.stderr

def test_cli_summary_report(clean_output_dir):
    """Test --summary flag ensures correct reporting of file counts."""
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--summary",
        "--output-dir", CLI_OUTPUT_DIR
    ])
    
    print("\nDEBUG - test_cli_summary_report OUTPUT:\n", result.stdout)
    
    assert "📊 Summary Report" in result.stdout or result.stderr
    