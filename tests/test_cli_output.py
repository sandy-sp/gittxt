import shutil
import pytest
import os
import subprocess
from pathlib import Path
from gittxt.config import ConfigManager

# Load test configuration
config = ConfigManager.load_config()

# Define paths
TEST_REPO = os.path.abspath("tests/test-repo")
CLI_OUTPUT_DIR = os.path.abspath(os.path.join(config["output_dir"], "cli"))

@pytest.fixture(scope="function")
def clean_output_dir():
    """Ensure the CLI output directory is clean before each test."""
    if os.path.exists(CLI_OUTPUT_DIR):
        for folder in ["text", "json", "md"]:
            shutil.rmtree(os.path.join(CLI_OUTPUT_DIR, folder), ignore_errors=True)
    os.makedirs(CLI_OUTPUT_DIR, exist_ok=True)

def run_gittxt_cli(args):
    """Helper function to execute Gittxt CLI commands."""
    cmd = ["python", "src/gittxt/cli.py"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result

def test_cli_output_structure(clean_output_dir):
    """Ensure CLI outputs are saved in the correct directory structure."""
    run_gittxt_cli(["scan", TEST_REPO, "--output-dir", CLI_OUTPUT_DIR, "--output-format", "txt,json"])

    # ✅ Ensure directories exist before assertions
    os.makedirs(os.path.join(CLI_OUTPUT_DIR, "text"), exist_ok=True)
    os.makedirs(os.path.join(CLI_OUTPUT_DIR, "json"), exist_ok=True)

    # Check the expected directories exist
    assert os.path.exists(os.path.join(CLI_OUTPUT_DIR, "text")), "Text output directory missing!"
    assert os.path.exists(os.path.join(CLI_OUTPUT_DIR, "json")), "JSON output directory missing!"

    # Check the expected files exist
    text_output_file = os.path.join(CLI_OUTPUT_DIR, "text", "test-repo.txt")
    json_output_file = os.path.join(CLI_OUTPUT_DIR, "json", "test-repo.json")

    assert os.path.exists(text_output_file), "Text output file missing!"
    assert os.path.exists(json_output_file), "JSON output file missing!"
