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
            str(TEST_REPO),
            "--output-format", "txt,json",
            "--zip",
            "--lite",
            "--output-dir", str(OUTPUT_DIR)
        ],
        capture_output=True,
        text=True
    )

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    assert result.returncode == 0, f"CLI returned error code {result.returncode}"
    assert "✅ Scan complete" in result.stdout or "📄 Output generated" in result.stdout

    # Validate outputs created
    txt_files = list(OUTPUT_DIR.rglob("*.txt"))
    json_files = list(OUTPUT_DIR.rglob("*.json"))
    zip_files = list(OUTPUT_DIR.rglob("*.zip"))

    assert txt_files, "Expected .txt output not found"
    assert json_files, "Expected .json output not found"
    assert zip_files, "Expected .zip output not found"
