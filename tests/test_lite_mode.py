import pytest
from pathlib import Path
from gittxt.core.output_builder import OutputBuilder
from gittxt.core.scanner import Scanner

TEST_REPO = Path("test_repo")
OUTPUT_DIR = Path("test_outputs_lite")

@pytest.mark.asyncio
async def test_lite_output_formatting():
    scanner = Scanner(root_path=TEST_REPO)
    all_files = await scanner.scan_directory()

    builder = OutputBuilder(
        repo_name="test_repo",
        output_dir=OUTPUT_DIR,
        output_format="txt,md,json",
        repo_url="https://github.com/test-user/test_repo",
        branch="main",
        subdir="",
        mode="lite"
    )

    outputs = await builder.generate_output(all_files, repo_path=TEST_REPO)

    for out in outputs:
        text = out.read_text(encoding="utf-8")
        assert "Summary" not in text
        assert "Tokens" not in text
        assert "Assets" not in text
        assert "script.py" in text or "README.md" in text

        if out.suffix == ".md":
            assert "# Gittxt Lite Report" in text
            assert "```text" in text
        elif out.suffix == ".json":
            assert '"repository"' in text
            assert '"files"' in text
            assert '"summary"' not in text
