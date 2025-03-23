import pytest
from gittxt.output_builder import OutputBuilder
from gittxt.utils.filetype_utils import classify_file

@pytest.mark.asyncio
async def test_output_builder_all_formats(tmp_path, test_repo):
    repo_name = "test-repo"
    repo_path = test_repo

    # Pre-classify files into TEXTUAL and NON-TEXTUAL
    text_files = []
    non_textual_files = []
    for file in repo_path.rglob("*"):
        if not file.is_file():
            continue
        classification = classify_file(file)
        if classification in {"code", "docs", "configs", "data"}:
            text_files.append(file)
        else:
            non_textual_files.append(file)

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=tmp_path,
        output_format="txt,json,md"
    )

    # Run formatter & ZIP generation together
    await builder.generate_output(
        all_files=text_files + non_textual_files,
        repo_path=repo_path,
        create_zip=True,
        tree_depth=None
    )

    assert (tmp_path / "text").exists()
    assert (tmp_path / "json").exists()
    assert (tmp_path / "md").exists()
    assert (tmp_path / "zips").exists()
