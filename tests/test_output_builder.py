import pytest
import json
import shutil
from pathlib import Path
from gittxt.output_builder import OutputBuilder

TEST_REPO_NAME = "test-repo"
TEST_OUTPUT_DIR = Path("tests") / "gittxt-outputs"
TEST_TEXT_FILE = TEST_OUTPUT_DIR / "text" / f"{TEST_REPO_NAME}.txt"
TEST_JSON_FILE = TEST_OUTPUT_DIR / "json" / f"{TEST_REPO_NAME}.json"
TEST_MARKDOWN_FILE = TEST_OUTPUT_DIR / "md" / f"{TEST_REPO_NAME}.md"
MOCK_FILES = ["file1.py", "file2.md", "file3.log"]

@pytest.fixture(scope="function")
def clean_output_dir():
    for subdir in ["text", "json", "md"]:
        output_path = TEST_OUTPUT_DIR / subdir
        if output_path.exists():
            shutil.rmtree(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

@pytest.fixture
def mock_file_system(tmp_path):
    repo_path = tmp_path / TEST_REPO_NAME
    repo_path.mkdir()
    for file in MOCK_FILES:
        (repo_path / file).write_text("Mock content for testing.", encoding="utf-8")
    return repo_path

def test_generate_text_output(clean_output_dir, mock_file_system):
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="txt")
    output_paths = builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)
    output_file = Path(output_paths[0])
    assert output_file.exists()
    assert "📂 Repository Structure Overview" in output_file.read_text(encoding="utf-8")
    assert "Mock content for testing." in output_file.read_text(encoding="utf-8")

def test_generate_json_output(clean_output_dir, mock_file_system):
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="json")
    output_paths = builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)
    output_file = Path(output_paths[0])
    assert output_file.exists()
    json_data = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(json_data["files"]) == len(MOCK_FILES)
    assert json_data["files"][0]["content"] == "Mock content for testing."

def test_handle_missing_files(clean_output_dir):
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="txt")
    missing_file = TEST_OUTPUT_DIR / "text" / "missing_file.txt"
    output_paths = builder.generate_output([missing_file], TEST_OUTPUT_DIR)
    output_file = Path(output_paths[0])
    assert output_file.exists()
    assert "[Error: File" in output_file.read_text(encoding="utf-8")

def test_max_lines_limited_output(clean_output_dir, mock_file_system):
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="txt", max_lines=1)
    output_paths = builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)
    output_file = Path(output_paths[0])
    content_lines = output_file.read_text(encoding="utf-8").splitlines()
    assert sum(1 for line in content_lines if "Mock content" in line) == len(MOCK_FILES)

def test_output_directory_structure():
    for subdir in ["text", "json", "md"]:
        assert (TEST_OUTPUT_DIR / subdir).exists()

def test_generate_markdown_output(clean_output_dir, mock_file_system):
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="md")
    output_paths = builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)
    output_file = Path(output_paths[0])
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "# 📂 Repository Overview:" in content
    assert "## 📜 Folder Structure" in content
    assert "Mock content for testing." in content

def test_multi_format_output(clean_output_dir, mock_file_system):
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="txt,json")
    output_paths = [Path(p) for p in builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)]
    assert any("text" in str(p) for p in output_paths)
    assert any("json" in str(p) for p in output_paths)
    for path in output_paths:
        assert path.exists()
