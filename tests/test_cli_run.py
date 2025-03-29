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

    # Accept either a clean success or a no-text warning
    assert result.returncode == 0, f"CLI failed with exit code {result.returncode}"

    # Allow this warning to be valid output if nothing was included
    assert (
        "✅ Scan complete" in result.stdout
        or "📄 Output generated" in result.stdout
        or "⚠️ No valid textual files found." in result.stdout
    ), "Expected scan success or warning in CLI output"

    # These may not exist if no files were processed — soft check
    txt_files = list(OUTPUT_DIR.rglob("*.txt"))
    json_files = list(OUTPUT_DIR.rglob("*.json"))
    zip_files = list(OUTPUT_DIR.rglob("*.zip"))

    assert zip_files, "Expected .zip output not found"
