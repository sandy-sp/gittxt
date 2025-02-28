import pytest
import os
import subprocess
from gittxt.config import ConfigManager

# Load test configuration
config = ConfigManager.load_config()

# Define test repository and output paths
TEST_REPO = "tests/test-repo"
TEST_OUTPUT_DIR = os.path.join(config["output_dir"], "test-cli")

@pytest.fixture(scope="function")
def clean_output_dir():
    """Ensure the test output directory is clean before each test."""
    if os.path.exists(TEST_OUTPUT_DIR):
        for file in os.listdir(TEST_OUTPUT_DIR):
            file_path = os.path.join(TEST_OUTPUT_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(TEST_OUTPUT_DIR, exist_ok=True)

def run_gittxt_command(args):
    """Helper function to execute Gittxt CLI commands."""
    cmd = ["python", "src/gittxt/cli.py"] + args
    return subprocess.run(cmd, capture_output=True, text=True)

def test_cli_help():
    """Test if the CLI help command works."""
    result = run_gittxt_command(["--help"])
    assert "Usage: cli.py [OPTIONS] SOURCE" in result.stdout

def test_cli_basic_scan(clean_output_dir):
    """Test basic scanning of a local repository."""
    result = run_gittxt_command([TEST_REPO, "--output-dir", TEST_OUTPUT_DIR])
    assert "✅ Processing" in result.stdout
    assert os.path.exists(os.path.join(TEST_OUTPUT_DIR, "test-repo.txt"))

def test_cli_include_exclude(clean_output_dir):
    """Test if --include and --exclude options work correctly."""
    result = run_gittxt_command([
        TEST_REPO, "--include", ".py,.md",
        "--exclude", "node_modules,__pycache__",
        "--output-dir", TEST_OUTPUT_DIR
    ])
    assert "✅ Processing" in result.stdout
    assert os.path.exists(os.path.join(TEST_OUTPUT_DIR, "test-repo.txt"))

def test_cli_output_format_json(clean_output_dir):
    """Test if the JSON output format works."""
    result = run_gittxt_command([
        TEST_REPO, "--output-format", "json", "--output-dir", TEST_OUTPUT_DIR
    ])
    assert "✅ Output saved" in result.stdout
    assert os.path.exists(os.path.join(TEST_OUTPUT_DIR, "test-repo.json"))

def test_cli_summary_flag(clean_output_dir):
    """Test if --summary flag works correctly."""
    result = run_gittxt_command([
        TEST_REPO, "--summary", "--output-dir", TEST_OUTPUT_DIR
    ])
    assert "📊 Summary Report" in result.stdout

def test_cli_debug_flag(clean_output_dir):
    """Test if --debug flag enables debug mode."""
    result = run_gittxt_command([
        TEST_REPO, "--debug", "--output-dir", TEST_OUTPUT_DIR
    ])
    assert "🔍 Debug mode enabled." in result.stdout
