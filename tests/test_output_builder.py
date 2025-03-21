import shutil
import zipfile
import json
from pathlib import Path, PurePath
import pytest
import asyncio
from gittxt.output_builder import OutputBuilder

@pytest.fixture(scope="function")
def output_dir(tmp_path):
    out_dir = tmp_path / "test-outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir

@pytest.fixture
def mock_repo(tmp_path):
    repo = tmp_path / "mock-repo"
    (repo / "assets").mkdir(parents=True)
    (repo / "app.py").write_text("print('Hello')")
    (repo / "README.md").write_text("# Documentation")
    (repo / "assets/data.csv").write_text("id,value\n1,200")
    (repo / "assets/logo.png").write_bytes(b"\x89PNG\r\n")
    return repo

@pytest.mark.asyncio
async def test_txt_formatter_metadata(output_dir, mock_repo):
    builder = OutputBuilder("mock-repo", output_dir=output_dir, output_format="txt")
    await builder.generate_output(list(mock_repo.rglob("*")), mock_repo)
    txt_file = output_dir / "text" / "mock-repo.txt"
    content = txt_file.read_text()
    assert txt_file.exists()
    assert "Gittxt Report" in content
    assert "SHA256" in content
    assert "📊 Summary Report" in content
    assert "Tokens By Type" in content

@pytest.mark.asyncio
async def test_json_formatter_file_hashes(output_dir, mock_repo):
    builder = OutputBuilder("mock-repo", output_dir=output_dir, output_format="json")
    await builder.generate_output(list(mock_repo.rglob("*")), mock_repo)
    json_file = output_dir / "json" / "mock-repo.json"
    assert json_file.exists()
    data = json.loads(json_file.read_text())
    assert "metadata" in data
    assert "files" in data
    for file_entry in data["files"]:
        assert "sha256" in file_entry
        assert len(file_entry["sha256"]) >= 8

@pytest.mark.asyncio
async def test_md_formatter_code_blocks(output_dir, mock_repo):
    builder = OutputBuilder("mock-repo", output_dir=output_dir, output_format="md")
    await builder.generate_output(list(mock_repo.rglob("*")), mock_repo)
    md_file = output_dir / "md" / "mock-repo.md"
    assert md_file.exists()
    content = md_file.read_text()
    assert "Generated:" in content
    assert "```python" in content or "```" in content
    assert "SHA256" in content
    assert "Tokens by Type" in content

@pytest.mark.asyncio
async def test_zip_bundle_includes_outputs(output_dir, mock_repo):
    builder = OutputBuilder("mock-repo", output_dir=output_dir, output_format="txt,json,md")
    await builder.generate_output(list(mock_repo.rglob("*")), mock_repo, create_zip=True)

    zip_file = output_dir / "zips" / "mock-repo_bundle.zip"
    assert zip_file.exists()

    with zipfile.ZipFile(zip_file, "r") as zf:
        zip_contents = zf.namelist()
        basenames = [PurePath(p).name for p in zip_contents]
        assert "mock-repo.txt" in basenames
        assert "mock-repo.json" in basenames
        assert "mock-repo.md" in basenames
        assert "logo.png" in basenames
        assert any(p.endswith("data.csv") for p in zip_contents)

@pytest.mark.asyncio
async def test_handle_empty_files_list(output_dir, mock_repo):
    builder = OutputBuilder("mock-repo", output_dir=output_dir, output_format="txt")
    empty = await builder.generate_output([], mock_repo)
    assert isinstance(empty, list)
