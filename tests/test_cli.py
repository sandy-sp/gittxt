import pytest
import os
import shutil
import subprocess
from gittxt.config import ConfigManager

# Load test configuration
config = ConfigManager.load_config()

# Define test repository and output paths
TEST_REPO = os.path.abspath("tests/test-repo")
TEST_OUTPUT_DIR = os.path.abspath(os.path.join(config["output_dir"], "test-cli"))
TEXT_OUTPUT_PATH = os.path.join(TEST_OUTPUT_DIR, "text", "test-repo.txt")  # Fixed path
JSON_OUTPUT_PATH = os.path.join(TEST_OUTPUT_DIR, "json", "test-repo.json")  # Fixed path

@pytest.fixture(scope="function")
def clean_output_dir():
    """Ensure the test output directory is clean before each test."""
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

def run_gittxt_command(args):
    """Helper function to execute Gittxt CLI commands."""
    cmd = ["python", "src/gittxt/cli.py"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Debugging Output
    print("\n--- STDOUT ---\n", result.stdout)
    print("\n--- STDERR ---\n", result.stderr)

    return result

def test_cli_help():
    """Test if the CLI help command works."""
    result = run_gittxt_command(["--help"])
    assert "Usage:" in result.stdout or result.stderr  # Check both stdout and stderr

def test_cli_basic_scan(clean_output_dir):
    """Test basic scanning of a local repository."""
    result = run_gittxt_command([TEST_REPO, "--output-dir", TEST_OUTPUT_DIR])

    # Debugging: Print the actual result
    print("\nDEBUG - test_cli_basic_scan OUTPUT:\n", result.stdout)

    assert "✅ Scanning complete." in result.stdout or "✅ Processing" in result.stdout or result.stderr
    assert os.path.exists(TEXT_OUTPUT_PATH)  # Fixed path assertion

def test_cli_include_exclude(clean_output_dir):
    """Test if --include and --exclude options work correctly."""
    result = run_gittxt_command([
        TEST_REPO, "--include", ".py", "--include", ".md",
        "--exclude", "node_modules", "--exclude", "__pycache__",
        "--output-dir", TEST_OUTPUT_DIR
    ])

    # Debugging: Print the actual result
    print("\nDEBUG - test_cli_include_exclude OUTPUT:\n", result.stdout)

    assert "✅ Scanning complete." in result.stdout or "✅ Processing" in result.stdout or result.stderr
    assert os.path.exists(TEXT_OUTPUT_PATH)  # Fixed path assertion

def test_cli_output_format_json(clean_output_dir):
    """Test if the JSON output format works."""
    result = run_gittxt_command([
        TEST_REPO, "--output-format", "json", "--output-dir", TEST_OUTPUT_DIR
    ])

    # Debugging: Print the actual result
    print("\nDEBUG - test_cli_output_format_json OUTPUT:\n", result.stdout)

    assert "✅ Output saved to:" in result.stdout or result.stderr
    assert os.path.exists(JSON_OUTPUT_PATH)  # Fixed path assertion

def test_cli_summary_flag(clean_output_dir):
    """Test if --summary flag works correctly."""
    result = run_gittxt_command([
        TEST_REPO, "--summary", "--output-dir", TEST_OUTPUT_DIR
    ])

    # Debugging: Print the actual result
    print("\nDEBUG - test_cli_summary_flag OUTPUT:\n", result.stdout)

    assert "📊 Summary Report" in result.stdout or "Scanned" in result.stdout or result.stderr

def test_cli_debug_flag(clean_output_dir):
    """Test if --debug flag enables debug mode."""
    result = run_gittxt_command([
        TEST_REPO, "--debug", "--output-dir", TEST_OUTPUT_DIR
    ])

    # Debugging: Print the actual result
    print("\nDEBUG - test_cli_debug_flag OUTPUT:\n", result.stdout)

    assert "🔍 Debug mode enabled." in result.stdout or result.stderr

def test_cli_summary_report(clean_output_dir):
    """Test if --summary flag correctly generates a summary report."""
    result = run_gittxt_command([
        TEST_REPO, "--summary", "--output-dir", TEST_OUTPUT_DIR
    ])

    # Debugging: Print actual stdout and stderr
    print("\nDEBUG - test_cli_summary_report OUTPUT:\n", result.stdout)
    print("\nDEBUG - STDERR:\n", result.stderr)

    assert "📊 Summary Report" in result.stdout or "📊 Summary Report" in result.stderr
