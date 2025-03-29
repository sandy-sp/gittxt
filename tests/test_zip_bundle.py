import pytest
import zipfile
from pathlib import Path
from gittxt.core.scanner import Scanner
from gittxt.core.output_builder import OutputBuilder

TEST_REPO = Path("tests/test_repo")
OUTPUT_DIR = Path("tests/test_zip_output")

@pytest.mark.asyncio
async def test_zip_bundle_contents():
    scanner = Scanner(root_path=TEST_REPO, use_ignore_file=True)
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
        repo_path=TEST_REPO.resolve(),
        create_zip=True
    )

    zip_files = [f for f in outputs if f.suffix == ".zip"]
    assert zip_files, "No ZIP output generated"

    zip_path = zip_files[0]
    assert zip_path.exists(), "ZIP file does not exist"

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        print("📦 ZIP Contents:", names)

        assert any("README.md" in n for n in names), "README.md missing from ZIP"
        assert any(n.endswith("summary.json") for n in names), "summary.json missing"
        assert any(n.endswith("manifest.json") for n in names), "manifest.json missing"
        assert any(n.endswith(".txt") for n in names), ".txt output missing"
        assert any(n.endswith(".json") for n in names), ".json output missing"
        assert any(n.endswith(".md") for n in names), ".md output missing"
