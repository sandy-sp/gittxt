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
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--non-interactive"
    ])
    assert (OUTPUT_DIR / "text" / "test-repo.txt").exists()

def test_multi_format_scan(clean_output_dir):
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--output-format", "txt,json,md",
        "--non-interactive"
    ])
    assert (OUTPUT_DIR / "text" / "test-repo.txt").exists()
    assert (OUTPUT_DIR / "json" / "test-repo.json").exists()
    assert (OUTPUT_DIR / "md" / "test-repo.md").exists()

def test_summary_flag(clean_output_dir):
    result = run_gittxt(["scan", str(TEST_REPO), "--output-dir", str(OUTPUT_DIR), "--summary", "--non-interactive"])
    assert "📊 Processed" in result.stdout or result.stderr

def test_file_types_flag(clean_output_dir):
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--file-types", "code,docs",
        "--non-interactive"
    ])
    output_txt = (OUTPUT_DIR / "text" / "test-repo.txt").read_text()

    # Skip tree by splitting at first file block
    if "=== FILE: " in output_txt:
        tree_part, file_part = output_txt.split("=== FILE: ", 1)
    else:
        tree_part, file_part = output_txt, ""

    # Scan headers in file blocks only
    file_blocks = ["=== FILE: " + block for block in file_part.split("=== FILE: ") if block.strip()]
    file_headers = [block.split("=== FILE: ")[-1].split(" ===")[0].strip() for block in file_blocks]

    assert "app.py" in " ".join(file_headers)
    assert "README.md" in " ".join(file_headers)
    assert "data.csv" not in " ".join(file_headers)

def test_zip_generation(clean_output_dir):
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--file-types", "all",
        "--non-interactive"
    ])
    zip_path = OUTPUT_DIR / "zips" / "test-repo_extras.zip"
    assert zip_path.exists()

def test_exclude_pattern(clean_output_dir):
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--exclude", "docs",
        "--non-interactive"
    ])
    output_txt = (OUTPUT_DIR / "text" / "test-repo.txt").read_text()
    
    # Split into file content sections
    file_blocks = output_txt.split("=== ")
    file_content_blocks = [block for block in file_blocks if block.strip().startswith("docs/")]

    # overview.md should not appear in the content section
    assert not any("overview.md" in block for block in file_content_blocks)