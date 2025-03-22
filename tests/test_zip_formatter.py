import pytest
import asyncio
from gittxt.formatters.zip_formatter import ZipFormatter

@pytest.mark.asyncio
async def test_zip_formatter_creates_bundle(tmp_path):
    output_txt = tmp_path / "output.txt"
    output_json = tmp_path / "output.json"
    output_txt.write_text("Hello")
    output_json.write_text("{\"msg\": \"Hello\"}")

    asset_file = tmp_path / "assets" / "image.png"
    asset_file.parent.mkdir(parents=True)
    asset_file.write_bytes(b"FAKEPNGDATA")

    zip_formatter = ZipFormatter(
        repo_name="test-repo",
        output_dir=tmp_path,
        output_files=[output_txt, output_json],
        non_textual_files=[asset_file],
        repo_path=tmp_path
    )

    zip_path = await zip_formatter.generate()
    assert zip_path.exists()
    assert zip_path.name.endswith("_bundle.zip")
