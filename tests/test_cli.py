import pytest
import os
import shutil
import subprocess
from gittxt.config import ConfigManager

# Load test configuration
config = ConfigManager.load_config()

# Adjust these as needed for your local structure
TEST_REPO = os.path.abspath("tests/test-repo")
TEST_OUTPUT_DIR = os.path.abspath(os.path.join(config["output_dir"], "test-cli"))
TEXT_OUTPUT_PATH = os.path.join(TEST_OUTPUT_DIR, "text", "test-repo.txt")  # For single-format 'txt'
JSON_OUTPUT_PATH = os.path.join(TEST_OUTPUT_DIR, "json", "test-repo.json") # For single-format 'json'

@pytest.fixture(scope="function")
def clean_output_dir():
    """Ensure the test output directory is clean before each test."""
    if os.path.exists(TEST_OUTPUT_DIR):
        shutil.rmtree(TEST_OUTPUT_DIR)
    os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

def run_gittxt_command(args):
    """
    Helper function to execute Gittxt CLI commands.
    We'll always call the top-level script with subcommands, e.g.:
      ["scan", TEST_REPO, ...]
    or
      ["install"]
    """
    cmd = ["python", "src/gittxt/cli.py"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Debugging Output
    print("\n--- STDOUT ---\n", result.stdout)
    print("\n--- STDERR ---\n", result.stderr)

    return result

def test_cli_help():
    """
    Test if the CLI help command works at the top-level.
    Should display subcommands like 'install' and 'scan'.
    """
    result = run_gittxt_command(["--help"])
    assert "Usage:" in result.stdout or result.stderr
    assert "install" in result.stdout or result.stderr
    assert "scan" in result.stdout or result.stderr

def test_cli_basic_scan(clean_output_dir):
    """
    Test basic scanning of a local repository via the 'scan' subcommand.
    """
    # We'll do 'gittxt scan <repo> --output-dir ...'
    result = run_gittxt_command(["scan", TEST_REPO, "--output-dir", TEST_OUTPUT_DIR])

    print("\nDEBUG - test_cli_basic_scan OUTPUT:\n", result.stdout)

    # We expect some success message
    assert "✅ Processing" in result.stdout or result.stderr
    assert os.path.exists(TEXT_OUTPUT_PATH), "Expected text output file to be generated."

def test_cli_include_exclude(clean_output_dir):
    """
    Test if --include and --exclude options work correctly via 'scan'.
    """
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--include", ".py",
        "--include", ".md",
        "--exclude", "node_modules",
        "--exclude", "__pycache__",
        "--output-dir", TEST_OUTPUT_DIR
    ])

    print("\nDEBUG - test_cli_include_exclude OUTPUT:\n", result.stdout)

    assert "✅ Processing" in result.stdout or result.stderr
    assert os.path.exists(TEXT_OUTPUT_PATH), "Expected text output file to be generated."

def test_cli_output_format_json(clean_output_dir):
    """
    Test if the JSON output format works via 'scan'.
    """
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--output-format", "json",
        "--output-dir", TEST_OUTPUT_DIR
    ])

    print("\nDEBUG - test_cli_output_format_json OUTPUT:\n", result.stdout)

    # We expect "✅ Output saved to:" in the output
    assert "✅ Output saved to:" in result.stdout or result.stderr
    # Check for the JSON file
    assert os.path.exists(JSON_OUTPUT_PATH), "Expected JSON output file to be generated."

def test_cli_summary_flag(clean_output_dir):
    """
    Test if --summary flag works correctly.
    """
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--summary",
        "--output-dir", TEST_OUTPUT_DIR
    ])

    print("\nDEBUG - test_cli_summary_flag OUTPUT:\n", result.stdout)
    assert "📊 Summary Report" in result.stdout or result.stderr

def test_cli_debug_flag(clean_output_dir):
    """
    Test if --debug flag enables debug mode.
    """
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--debug",
        "--output-dir", TEST_OUTPUT_DIR
    ])

    print("\nDEBUG - test_cli_debug_flag OUTPUT:\n", result.stdout)
    # The new CLI logs "🔍 Debug mode enabled." if debug is set
    assert "🔍 Debug mode enabled." in result.stdout or result.stderr

def test_cli_summary_report(clean_output_dir):
    """
    Test if --summary flag correctly generates a summary report.
    """
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--summary",
        "--output-dir", TEST_OUTPUT_DIR
    ])

    print("\nDEBUG - test_cli_summary_report OUTPUT:\n", result.stdout)
    assert "📊 Summary Report" in result.stdout or result.stderr

# Optional: Test multi-format
def test_cli_multi_format(clean_output_dir):
    """
    Test scanning with multiple output formats (txt,json).
    """
    result = run_gittxt_command([
        "scan", TEST_REPO,
        "--output-format", "txt,json",
        "--output-dir", TEST_OUTPUT_DIR
    ])
    print("\nDEBUG - test_cli_multi_format OUTPUT:\n", result.stdout)

    # Check for both .txt and .json
    assert os.path.exists(TEXT_OUTPUT_PATH), "Expected text output file in multi-format mode."
    assert os.path.exists(JSON_OUTPUT_PATH), "Expected JSON output file in multi-format mode."

