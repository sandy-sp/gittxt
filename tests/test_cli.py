import pytest
import shutil
import subprocess
from pathlib import Path
from gittxt.config import ConfigManager

config = ConfigManager.load_config()

TEST_REPO = Path("tests/test-repo").resolve()
TEST_OUTPUT_DIR = Path(config["output_dir"]) / "test-cli"
TEXT_OUTPUT_PATH = TEST_OUTPUT_DIR / "text" / "test-repo.txt"
JSON_OUTPUT_PATH = TEST_OUTPUT_DIR / "json" / "test-repo.json"

@pytest.fixture(scope="function")
def clean_output_dir():
    if TEST_OUTPUT_DIR.exists():
        shutil.rmtree(TEST_OUTPUT_DIR)
    TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def run_gittxt_command(args):
    cmd = ["python", "src/gittxt/cli.py"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("\n--- STDOUT ---\n", result.stdout)
    print("\n--- STDERR ---\n", result.stderr)
    return result

def test_cli_help():
    result = run_gittxt_command(["--help"])
    assert "Usage:" in result.stdout or result.stderr
    assert "install" in result.stdout or result.stderr
    assert "scan" in result.stdout or result.stderr

def test_cli_basic_scan(clean_output_dir):
    result = run_gittxt_command(["scan", str(TEST_REPO), "--output-dir", str(TEST_OUTPUT_DIR)])
    assert "✅ Processing" in result.stdout or result.stderr
    assert TEXT_OUTPUT_PATH.exists()

def test_cli_include_exclude(clean_output_dir):
    result = run_gittxt_command([
        "scan", str(TEST_REPO),
        "--include", ".py",
        "--include", ".md",
        "--exclude", "node_modules",
        "--exclude", "__pycache__",
        "--output-dir", str(TEST_OUTPUT_DIR)
    ])
    assert "✅ Processing" in result.stdout or result.stderr
    assert TEXT_OUTPUT_PATH.exists()

def test_cli_output_format_json(clean_output_dir):
    result = run_gittxt_command([
        "scan", str(TEST_REPO),
        "--output-format", "json",
        "--output-dir", str(TEST_OUTPUT_DIR)
    ])
    assert "✅ Output saved to:" in result.stdout or result.stderr
    assert JSON_OUTPUT_PATH.exists()

def test_cli_summary_flag(clean_output_dir):
    result = run_gittxt_command([
        "scan", str(TEST_REPO),
        "--summary",
        "--output-dir", str(TEST_OUTPUT_DIR)
    ])
    assert "📊 Summary Report" in result.stdout or result.stderr

def test_cli_debug_flag(clean_output_dir):
    result = run_gittxt_command([
        "scan", str(TEST_REPO),
        "--debug",
        "--output-dir", str(TEST_OUTPUT_DIR)
    ])
    assert "🔍 Debug mode enabled." in result.stdout or result.stderr

def test_cli_summary_report(clean_output_dir):
    result = run_gittxt_command([
        "scan", str(TEST_REPO),
        "--summary",
        "--output-dir", str(TEST_OUTPUT_DIR)
    ])
    assert "📊 Summary Report" in result.stdout or result.stderr

def test_cli_multi_format(clean_output_dir):
    result = run_gittxt_command([
        "scan", str(TEST_REPO),
        "--output-format", "txt,json",
        "--output-dir", str(TEST_OUTPUT_DIR)
    ])
    assert TEXT_OUTPUT_PATH.exists()
    assert JSON_OUTPUT_PATH.exists()
