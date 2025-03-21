import subprocess
import shutil
from pathlib import Path
import pytest

TEST_REPO = Path("tests/test-repo").resolve()
OUTPUT_DIR = Path("tests/test-outputs")


@pytest.fixture(scope="function")
def clean_output_dir():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_gittxt(args):
    cmd = ["python", "src/gittxt/cli.py"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("\n--- STDOUT ---\n", result.stdout)
    print("\n--- STDERR ---\n", result.stderr)
    return result


def test_basic_scan_txt(clean_output_dir):
    run_gittxt(
        ["scan", str(TEST_REPO), "--output-dir", str(OUTPUT_DIR), "--non-interactive"]
    )
    assert (OUTPUT_DIR / "text" / "test-repo.txt").exists()


def test_multi_format_scan(clean_output_dir):
    run_gittxt(
        [
            "scan",
            str(TEST_REPO),
            "--output-dir",
            str(OUTPUT_DIR),
            "--output-format",
            "txt,json,md",
            "--non-interactive",
        ]
    )
    assert (OUTPUT_DIR / "text" / "test-repo.txt").exists()
    assert (OUTPUT_DIR / "json" / "test-repo.json").exists()
    assert (OUTPUT_DIR / "md" / "test-repo.md").exists()


def test_summary_flag(clean_output_dir):
    output = run_gittxt(
        [
            "scan",
            str(TEST_REPO),
            "--output-dir",
            str(OUTPUT_DIR),
            "--summary",
            "--non-interactive",
        ]
    ).stdout

    # Normalize output once
    output_lower = output.lower()

    # Assert CLI summary structure
    assert "📊 summary report" in output_lower
    assert "total files processed" in output_lower
    assert "output formats:" in output_lower
    assert "file type breakdown" in output_lower


def test_file_types_flag(clean_output_dir):
    run_gittxt(
        [
            "scan",
            str(TEST_REPO),
            "--output-dir",
            str(OUTPUT_DIR),
            "--file-types",
            "code,docs",
            "--non-interactive",
        ]
    )
    output_txt = (OUTPUT_DIR / "text" / "test-repo.txt").read_text()

    # Skip tree by splitting at first file block
    if "=== FILE: " in output_txt:
        _, file_part = output_txt.split("=== FILE: ", 1)
    else:
        _, file_part = output_txt, ""

    # Scan headers in file blocks only
    file_blocks = [
        "=== FILE: " + block for block in file_part.split("=== FILE: ") if block.strip()
    ]
    file_headers = [
        block.split("=== FILE: ")[-1].split(" ===")[0].strip() for block in file_blocks
    ]

    assert "app.py" in " ".join(file_headers)
    assert "README.md" in " ".join(file_headers)
    assert "data.csv" not in " ".join(file_headers)


def test_zip_generation(clean_output_dir):
    run_gittxt(
        [
            "scan",
            str(TEST_REPO),
            "--output-dir",
            str(OUTPUT_DIR),
            "--file-types",
            "all",
            "--non-interactive",
        ]
    )
    zip_path = OUTPUT_DIR / "zips" / "test-repo_bundle.zip"
    assert zip_path.exists()


def test_exclude_pattern(clean_output_dir):
    run_gittxt(
        [
            "scan",
            str(TEST_REPO),
            "--output-dir",
            str(OUTPUT_DIR),
            "--exclude",
            "docs",
            "--non-interactive",
        ]
    )
    output_txt = (OUTPUT_DIR / "text" / "test-repo.txt").read_text()

    # Skip tree view, focus only on file content sections
    if "=== FILE: " in output_txt:
        _, file_part = output_txt.split("=== FILE: ", 1)
    else:
        _, file_part = output_txt, ""

    file_blocks = [
        "=== FILE: " + block for block in file_part.split("=== FILE: ") if block.strip()
    ]
    file_headers = [
        block.split("=== FILE: ")[-1].split(" ===")[0].strip() for block in file_blocks
    ]

    # Ensure overview.md is not in processed content (docs/ was excluded)
    assert not any("overview.md" in header for header in file_headers)
