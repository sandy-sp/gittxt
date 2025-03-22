from gittxt.output_builder import OutputBuilder
from gittxt.utils.tree_utils import generate_tree
from gittxt.utils.filetype_utils import classify_file
import asyncio

def test_output_builder_formats(tmp_path, test_repo):
    repo_name = "test-repo"
    repo_path = test_repo

    # Classify manually
    text_files = []
    asset_files = []
    for file in repo_path.rglob("*"):
        if not file.is_file():
            continue
        classification = classify_file(file)
        if classification in {"code", "docs", "csv"}:
            text_files.append(file)
        else:
            asset_files.append(file)

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=tmp_path,
        output_format="txt,json,md"
    )

    loop = asyncio.get_event_loop()
    result_files = loop.run_until_complete(
        builder.generate_output(text_files, asset_files, repo_path, create_zip=True, tree_depth=2)
    )

    # Validate outputs
    assert any(".txt" in str(f) for f in result_files)
    assert any(".json" in str(f) for f in result_files)
    assert any(".md" in str(f) for f in result_files)
    assert any(".zip" in str(f) for f in result_files)

    for fmt in ["text", "json", "md", "zips"]:
        assert (tmp_path / fmt).exists()

def test_output_builder_zip_contents(tmp_path, test_repo):
    repo_name = "test-repo"
    repo_path = test_repo

    text_files = []
    asset_files = []
    for file in repo_path.rglob("*"):
        if not file.is_file():
            continue
        classification = classify_file(file)
        if classification in {"code", "docs"}:
            text_files.append(file)
        else:
            asset_files.append(file)

    builder = OutputBuilder(
        repo_name=repo_name,
        output_dir=tmp_path,
        output_format="txt,json,md"
    )

    loop = asyncio.get_event_loop()
    result_files = loop.run_until_complete(
        builder.generate_output(text_files, asset_files, repo_path, create_zip=True, tree_depth=1)
    )

    # Validate relative paths inside ZIP
    zip_file = [f for f in result_files if str(f).endswith(".zip")][0]
    import zipfile
    with zipfile.ZipFile(zip_file, "r") as zipf:
        namelist = zipf.namelist()
        assert any("src/example.py" in name or "docs/README.md" in name for name in namelist)
