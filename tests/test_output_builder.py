import shutil
import zipfile
import json
from pathlib import Path
import pytest
from gittxt.output_builder import OutputBuilder

TEST_REPO_NAME = "test-repo"
OUTPUT_DIR = Path("tests/test-outputs")
MOCK_FILES = [
    "app.py",  # code
    "README.md",  # doc
    "assets/data.csv",  # csv
    "assets/logo.png",  # image
]


@pytest.fixture(scope="function")
def clean_output_dir():
    for subdir in ["text", "json", "md", "zips"]:
        out_dir = OUTPUT_DIR / subdir
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def mock_file_system(tmp_path):
    repo_path = tmp_path / TEST_REPO_NAME
    (repo_path / "assets").mkdir(parents=True)
    (repo_path / "app.py").write_text("print('Hello, World!')", encoding="utf-8")
    (repo_path / "README.md").write_text("# Mock README", encoding="utf-8")
    (repo_path / "assets/data.csv").write_text("id,value\n1,100", encoding="utf-8")
    (repo_path / "assets/logo.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    return repo_path


def test_generate_txt_output(clean_output_dir, mock_file_system):
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=OUTPUT_DIR, output_format="txt")
    builder.generate_output(list(mock_file_system.rglob("*")), mock_file_system)
    txt_path = OUTPUT_DIR / "text" / f"{TEST_REPO_NAME}.txt"
    assert txt_path.exists()
    content = txt_path.read_text()
    assert "📊 Summary Report:" in content


def test_generate_json_output(clean_output_dir, mock_file_system):
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=OUTPUT_DIR, output_format="json")
    builder.generate_output(list(mock_file_system.rglob("*")), mock_file_system)
    json_path = OUTPUT_DIR / "json" / f"{TEST_REPO_NAME}.json"
    assert json_path.exists()
    with json_path.open() as f:
        data = json.load(f)
        assert any("app.py" in file["file"] for file in data["files"])
        assert "summary" in data


def test_generate_markdown_output(clean_output_dir, mock_file_system):
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=OUTPUT_DIR, output_format="md")
    builder.generate_output(list(mock_file_system.rglob("*")), mock_file_system)
    md_path = OUTPUT_DIR / "md" / f"{TEST_REPO_NAME}.md"
    assert md_path.exists()
    content = md_path.read_text()
    assert "## 📊 Summary Report" in content


def test_zip_contains_output_and_assets(clean_output_dir, mock_file_system):
    builder = OutputBuilder(
        TEST_REPO_NAME, output_dir=OUTPUT_DIR, output_format="txt,json"
    )
    builder.generate_output(list(mock_file_system.rglob("*")), mock_file_system)

    zip_path = OUTPUT_DIR / "zips" / f"{TEST_REPO_NAME}_bundle.zip"
    assert zip_path.exists()

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zip_contents = zf.namelist()
        # Check processed files are inside
        assert any("test-repo.txt" in name for name in zip_contents)
        assert any("test-repo.json" in name for name in zip_contents)
        # Check non-text assets are inside
        assert any("assets/data.csv" in name or "data.csv" in name for name in zip_contents)
        assert any("assets/logo.png" in name or "logo.png" in name for name in zip_contents)