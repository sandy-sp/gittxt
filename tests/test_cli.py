import os
import shutil
import pytest
import subprocess

# Define paths
SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))  # `src/`
CLI_SCRIPT = os.path.join(SRC_DIR, "gittxt/cli.py")

# Define output directories
OUTPUT_DIR = os.path.join(SRC_DIR, "gittxt-outputs")
TEXT_DIR = os.path.join(OUTPUT_DIR, "text")
JSON_DIR = os.path.join(OUTPUT_DIR, "json")
CACHE_DIR = os.path.join(OUTPUT_DIR, "cache")

@pytest.fixture(scope="function")
def clean_output_dirs():
    """Ensure the output directories are clean before each test."""
    for folder in [TEXT_DIR, JSON_DIR, CACHE_DIR]:
        if os.path.exists(folder):
            shutil.rmtree(folder)  # Remove existing directory
        os.makedirs(folder, exist_ok=True)  # Recreate empty directory

@pytest.fixture
def test_local_repo(tmp_path):
    """Create a temporary directory with sample files for scanning."""
    test_repo = tmp_path / "test_repo"
    test_repo.mkdir()

    (test_repo / "file1.py").write_text("print('Hello from Python')")
    (test_repo / "file2.txt").write_text("Hello World in text file")
    (test_repo / "exclude.log").write_text("This file should be excluded")

    return str(test_repo)

def run_cli(args):
    """Run the CLI command with PYTHONPATH set."""
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC_DIR  # Ensure Python finds `gittxt`
    return subprocess.run(["python", CLI_SCRIPT] + args, capture_output=True, text=True, env=env)

def test_scan_local_directory(clean_output_dirs, test_local_repo):
    """Test scanning a local directory and generating `.txt` output."""
    result = run_cli([test_local_repo, "--format", "txt"])
    
    assert "✅ Found 3 valid files." in result.stdout  # Expect 3 valid files
    output_file = os.path.join(TEXT_DIR, "test_repo.txt")
    assert os.path.exists(output_file), "Text output file was not created"

def test_generate_json_output(clean_output_dirs, test_local_repo):
    """Test generating `.json` output."""
    result = run_cli([test_local_repo, "--format", "json"])

    assert "✅ Found 3 valid files." in result.stdout
    output_file = os.path.join(JSON_DIR, "test_repo.json")
    assert os.path.exists(output_file), "JSON output file was not created"

def test_force_rescan(clean_output_dirs, test_local_repo):
    """Test using `--force-rescan` to clear cache and reprocess files."""
    run_cli([test_local_repo, "--format", "txt"])

    # Run again with `--force-rescan`
    result = run_cli([test_local_repo, "--format", "txt", "--force-rescan"])

    assert "♻️ Cache cleared for test_repo. Performing a full rescan." in result.stdout
    assert "✅ Found 3 valid files." in result.stdout

def test_invalid_repo_path(clean_output_dirs):
    """Test handling an invalid repository path."""
    result = run_cli(["invalid_repo_path/"])

    assert "❌ Repository path does not exist: 'invalid_repo_path/'." in result.stdout  # Updated assertion
