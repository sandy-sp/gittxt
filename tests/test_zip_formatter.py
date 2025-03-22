from gittxt.formatters.zip_formatter import ZipFormatter
import asyncio
from zipfile import ZipFile

def test_zip_formatter_creates_bundle(tmp_path):
    # Simulate generated output files
    output_txt = tmp_path / "output.txt"
    output_json = tmp_path / "output.json"
    output_txt.write_text("Hello")
    output_json.write_text("{\"msg\": \"Hello\"}")

    # Simulate non-textual files to package under /assets
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

    loop = asyncio.get_event_loop()
    zip_path = loop.run_until_complete(zip_formatter.generate())
    assert zip_path.exists()

    # Validate ZIP contents
    with ZipFile(zip_path, "r") as z:
        files = z.namelist()
        assert "output.txt" in files
        assert "output.json" in files
        assert "README-gittxt.txt" in files
        assert "assets/assets/image.png" in files or "assets/image.png" in files  # structure fallback
