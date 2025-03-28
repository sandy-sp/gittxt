import pytest
from pathlib import Path
from gittxt.core.output_builder import OutputBuilder
from gittxt.core.scanner import Scanner

TEST_REPO = Path("test_repo")
OUTPUT_DIR = Path("test_outputs")

@pytest.mark.asyncio
async def test_output_builder_all_formats():
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

    outputs = await builder.generate_output(all_files, repo_path=TEST_REPO)

    assert outputs
    assert any(f.suffix == ".txt" for f in outputs)
    assert any(f.suffix == ".md" for f in outputs)
    assert any(f.suffix == ".json" for f in outputs)

    # Validate content of each output file
    for out in outputs:
        text = out.read_text(encoding="utf-8")
        if out.suffix == ".txt":
            assert "Gittxt Report" in text
            assert "README.md" in text
        elif out.suffix == ".md":
            assert "# 🧾 Gittxt Report" in text
            assert "## 📊 Summary Report" in text
        elif out.suffix == ".json":
            assert '"repository"' in text
            assert '"files"' in text
            assert '"summary"' in text
