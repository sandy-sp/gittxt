import subprocess
import shutil
from pathlib import Path
import json
import importlib
import pytest

TEST_REPO = Path("tests/test-repo").resolve()
OUTPUT_DIR = Path("tests/test-outputs")
FILETYPE_CONFIG = Path("filetype_config.json")


@pytest.fixture(scope="function")
def clean_output_dir():
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="function")
def reset_filetype_config():
    if FILETYPE_CONFIG.exists():
        FILETYPE_CONFIG.unlink()
    subprocess.run(["python", "src/gittxt/cli.py", "--help"], capture_output=True)


def run_gittxt(args):
    cmd = ["python", "src/gittxt/cli.py"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    print("\n--- STDOUT ---\n", result.stdout)
    print("\n--- STDERR ---\n", result.stderr)
    return result


def test_basic_scan_txt(clean_output_dir, reset_filetype_config):
    run_gittxt(["scan", str(TEST_REPO), "--output-dir", str(OUTPUT_DIR), "--non-interactive"])
    assert (OUTPUT_DIR / "text" / "test-repo.txt").exists()


def test_multi_format_scan(clean_output_dir, reset_filetype_config):
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


def test_summary_flag(clean_output_dir, reset_filetype_config):
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

    output_lower = output.lower()
    assert "📊 summary report" in output_lower
    assert "text-convertible files" in output_lower


def test_zip_generation_dynamic(clean_output_dir, reset_filetype_config):
    # Trigger dynamic asset collection
    run_gittxt(
        [
            "scan",
            str(TEST_REPO),
            "--output-dir",
            str(OUTPUT_DIR),
            "--non-interactive",
        ]
    )
    zip_path = OUTPUT_DIR / "zips" / "test-repo_bundle.zip"
    # Skip if repo has no assets
    if zip_path.exists():
        assert zip_path.stat().st_size > 0
    else:
        pytest.skip("No asset files found to trigger ZIP bundle.")


def test_exclude_pattern(clean_output_dir, reset_filetype_config):
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

    assert not any("overview.md" in header for header in file_headers)


# NEW TESTS FOR PIPELINE -------------------------

def test_dynamic_whitelist_update(clean_output_dir, reset_filetype_config):
    config = json.loads(FILETYPE_CONFIG.read_text())
    config["whitelist"].append(".customext")
    FILETYPE_CONFIG.write_text(json.dumps(config, indent=4))

    from gittxt.utils import filetype_utils
    importlib.reload(filetype_utils)

    dummy_file = Path("dummy.customext")
    dummy_file.write_text("print('custom text')")
    result = filetype_utils.classify_file(dummy_file)
    dummy_file.unlink()

    assert result == "text"
    config = json.loads(FILETYPE_CONFIG.read_text())
    assert ".customext" in config["whitelist"]


def test_blacklist_enforcement(clean_output_dir, reset_filetype_config):
    config = json.loads(FILETYPE_CONFIG.read_text())
    config["blacklist"].append(".weirdbin")
    FILETYPE_CONFIG.write_text(json.dumps(config, indent=4))

    from gittxt.utils import filetype_utils
    importlib.reload(filetype_utils)

    dummy_file = Path("dummy.weirdbin")
    dummy_file.write_bytes(b"\x00\x01\x02")
    result = filetype_utils.classify_file(dummy_file)
    dummy_file.unlink()

    assert result == "asset"
    config = json.loads(FILETYPE_CONFIG.read_text())
    assert ".weirdbin" in config["blacklist"]
