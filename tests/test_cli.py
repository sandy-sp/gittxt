import os
import subprocess
import shutil
from pathlib import Path
import pytest

TEST_REPO = Path("tests/test-repo").resolve()
OUTPUT_DIR = Path("tests/test-outputs")
os.environ["GITTXT_OUTPUT_DIR"] = str(OUTPUT_DIR)

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

def test_scan_basic_txt(clean_output_dir):
    result = run_gittxt(["scan", str(TEST_REPO), "--output-dir", str(OUTPUT_DIR), "--non-interactive"])
    assert (OUTPUT_DIR / "text" / "test-repo.txt").exists()
    assert result.returncode == 0

def test_scan_all_formats(clean_output_dir):
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--output-format", "txt,json,md",
        "--non-interactive"
    ])
    assert (OUTPUT_DIR / "text" / "test-repo.txt").exists()
    assert (OUTPUT_DIR / "json" / "test-repo.json").exists()
    assert (OUTPUT_DIR / "md" / "test-repo.md").exists()
    assert result.returncode == 0

def test_scan_with_summary(clean_output_dir):
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--summary",
        "--non-interactive"
    ])
    assert "📊 Summary Report" in result.stdout
    assert result.returncode == 0

def test_scan_with_exclude(clean_output_dir):
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--exclude", "nested",
        "--non-interactive"
    ])
    txt_output = (OUTPUT_DIR / "text" / "test-repo.txt").read_text()
    assert "nested/level1/level2/level3/deep_file.py" not in txt_output
    assert result.returncode == 0

def test_scan_empty_repo_error():
    empty_dir = Path("tests/test-repo/empty-folder").resolve()
    result = run_gittxt(["scan", str(empty_dir), "--non-interactive"])
    assert "⚠️ No valid files found" in result.stderr or result.stdout
    assert result.returncode == 0

def test_classify_command():
    target_file = TEST_REPO / "app.py"
    result = run_gittxt(["classify", str(target_file)])
    assert "classified as: code" in result.stdout

def test_tree_command():
    result = run_gittxt(["tree", str(TEST_REPO)])
    assert "├── app.py" in result.stdout

def test_clean_command():
    (OUTPUT_DIR / "dummy.txt").write_text("temp file")
    result = run_gittxt(["clean", "--output-dir", str(OUTPUT_DIR)])
    assert not (OUTPUT_DIR / "text").exists()
    assert "Cleaned output directory" in result.stdout

def test_invalid_repo_url_error():
    dummy_url = "https://dummy-url-for-tests.com/invalid-repo.git"
    result = run_gittxt(["scan", dummy_url, "--non-interactive"])
    assert "❌ Repository resolution failed" in result.stdout or result.stderr

def test_valid_repo_url_error():
    valid_url = "https://github.com/sandy-sp/gittxt"
    result = run_gittxt(["scan", valid_url, "--non-interactive"])
    assert "✅ Gittxt scan completed" in result.stdout or result.stderr

def test_missing_repo_argument():
    result = run_gittxt(["scan", "--non-interactive"])
    assert "❌ No repositories specified" in result.stdout

# 🔴 NEW TEST: CLI --file-types filtering
def test_scan_with_file_types_code_only(clean_output_dir):
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--file-types", "code",
        "--output-format", "txt",
        "--non-interactive"
    ])
    txt_output = (OUTPUT_DIR / "text" / "test-repo.txt").read_text()
    assert "README.md" not in txt_output  # should filter out docs
    assert "app.py" in txt_output
    assert result.returncode == 0

def test_scan_with_file_types_docs_only(clean_output_dir):
    result = run_gittxt([
        "scan", str(TEST_REPO),
        "--output-dir", str(OUTPUT_DIR),
        "--file-types", "docs",
        "--output-format", "txt",
        "--non-interactive"
    ])
    txt_output = (OUTPUT_DIR / "text" / "test-repo.txt").read_text()
    assert "README.md" in txt_output
    assert "app.py" not in txt_output
    assert result.returncode == 0
