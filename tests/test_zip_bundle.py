import pytest
import zipfile
from pathlib import Path
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder

TEST_REPO = Path("test_repo")
OUTPUT_DIR = Path("test_zip_output")

@pytest.mark.asyncio
async def test_zip_bundle_contents():
    scanner = Scanner(root_path=TEST_REPO)
    all_files = await scanner.scan_directory()

    builder = OutputBuilder(
        repo_name="test_repo",
        output_dir=OUTPUT_DIR,
        output_format="txt,json,md",
        repo_url="https://github.com/test-user/test_repo",
        branch="main",
        subdir="",
        mode="rich"
    )

    outputs = await builder.generate_output(
        all_files,
        repo_path=TEST_REPO,
        create_zip=True
    )

    zip_files = [f for f in outputs if f.suffix == ".zip"]
    assert zip_files, "No ZIP output generated"
    zip_path = zip_files[0]

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        assert "README.md" in names
        assert "summary.json" in names
        assert "manifest.json" in names
        assert any(n.startswith("outputs/") and n.endswith(".txt") for n in names)
        assert any(n.startswith("outputs/") and n.endswith(".json") for n in names)
