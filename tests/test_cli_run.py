import subprocess
import pytest
from pathlib import Path

TEST_REPO = Path("tests/test_repo")
OUTPUT_DIR = Path("tests/cli_test_outputs")

def test_cli_scan_lite_zip():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "gittxt", "scan",
            str(REPO_DIR),
            "--output", "txt,json",
            "--zip",
            "--lite",
            "--output-dir", str(OUTPUT_DIR)
        ],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "✅ Scan complete" in result.stdout

    txt_files = list(OUTPUT_DIR.rglob("*.txt"))
    json_files = list(OUTPUT_DIR.rglob("*.json"))
    zip_files = list(OUTPUT_DIR.rglob("*.zip"))

    assert txt_files, "No .txt output found"
    assert json_files, "No .json output found"
    assert zip_files, "No .zip output found"
