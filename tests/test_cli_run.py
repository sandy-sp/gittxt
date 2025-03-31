import zipfile
import subprocess
import tempfile
import shutil
from pathlib import Path

TEST_REPO = Path("tests/test_repo")
OUTPUT_DIR = Path("tests/cli_test_outputs")


def test_cli_scan_lite_zip():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        [
            "gittxt",
            "scan",
            str(TEST_REPO),
            "--output-format",
            "txt,json",
            "--zip",
            "--lite",
            "--output-dir",
            str(OUTPUT_DIR),
        ],
        capture_output=True,
        text=True,
    )

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    # Accept a clean success or no-text warning
    assert result.returncode == 0, f"CLI failed with code {result.returncode}"

    assert (
        "✅ Scan complete" in result.stdout
        or "📄 Output generated" in result.stdout
        or "⚠️ No valid textual files found." in result.stdout
    ), "Expected scan success or valid warning"

    # Soft file check: files may be skipped by .gittxtignore
    txt_files = list(OUTPUT_DIR.rglob("*.txt"))
    json_files = list(OUTPUT_DIR.rglob("*.json"))
    zip_files = list(OUTPUT_DIR.rglob("*.zip"))

    assert zip_files, "Expected .zip output not found"
    assert any(
        f.name.endswith(".txt") for f in txt_files
    ), "Expected .txt output missing"
    assert any(
        f.name.endswith(".json") for f in json_files
    ), "Expected .json output missing"

def test_zip_bundle_contains_expected_files():
    # Setup temp output directory
    with tempfile.TemporaryDirectory() as temp_out:
        repo_url = "https://github.com/cyclotruc/gitingest"
        output_dir = Path(temp_out)

        # Run the CLI with --zip
        result = subprocess.run(
            [
                "gittxt",
                "scan",
                repo_url,
                "--zip",
                "--output-dir",
                str(output_dir),
                "--output-format",
                "txt"
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Failed: {result.stderr}"

        # Locate ZIP
        zip_files = list(output_dir.glob("*.zip"))
        assert zip_files, "No ZIP file created"
        zip_path = zip_files[0]

        with zipfile.ZipFile(zip_path, "r") as z:
            names = z.namelist()
            assert any("manifest.json" in f for f in names), "Missing manifest.json"
            assert any("summary.json" in f or "README.md" in f for f in names), "Missing summary or README"
            assert any("output.txt" in f for f in names), "Missing output.txt"
