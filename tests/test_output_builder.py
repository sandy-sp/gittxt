import asyncio
from gittxt.output_builder import OutputBuilder
from gittxt.utils.filetype_utils import classify_file

def test_output_builder_all_formats(tmp_path, test_repo):
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
    loop = asyncio.get_event_loop()
    result_files = loop.run_until_complete(
        builder.generate_output(text_files + non_textual_files, repo_path, create_zip=True, tree_depth=2)
    )

    # Validate file generation
    assert any(str(f).endswith(".txt") for f in result_files)
    assert any(str(f).endswith(".json") for f in result_files)
    assert any(str(f).endswith(".md") for f in result_files)
    assert any(str(f).endswith(".zip") for f in result_files)

    # Check folder creation
    assert (tmp_path / "text").exists()
    assert (tmp_path / "json").exists()
    assert (tmp_path / "md").exists()
    assert (tmp_path / "zips").exists()
