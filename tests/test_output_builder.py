import pytest
import os
import json
import shutil
from gittxt.output_builder import OutputBuilder

# Define test parameters
TEST_REPO_NAME = "test-repo"
TEST_OUTPUT_DIR = os.path.abspath("tests/gittxt-outputs")
TEST_TEXT_FILE = os.path.join(TEST_OUTPUT_DIR, "text", f"{TEST_REPO_NAME}.txt")
TEST_JSON_FILE = os.path.join(TEST_OUTPUT_DIR, "json", f"{TEST_REPO_NAME}.json")
TEST_MARKDOWN_FILE = os.path.join(TEST_OUTPUT_DIR, "md", f"{TEST_REPO_NAME}.md")
MOCK_FILES = ["file1.py", "file2.md", "file3.log"]

@pytest.fixture(scope="function")
def clean_output_dir():
    """Ensure the test output directory is clean before each test."""
    for subdir in ["text", "json", "md"]:
        output_path = os.path.join(TEST_OUTPUT_DIR, subdir)
        if os.path.exists(output_path):
            shutil.rmtree(output_path)
        os.makedirs(output_path, exist_ok=True)

@pytest.fixture
def mock_file_system(tmp_path):
    """Create a temporary directory with mock text and non-text files."""
    repo_path = tmp_path / TEST_REPO_NAME
    repo_path.mkdir()
    
    for file in MOCK_FILES:
        file_path = repo_path / file
        file_path.write_text("Mock content for testing.", encoding="utf-8")

    return repo_path

def test_generate_text_output(clean_output_dir, mock_file_system):
    """Test if text output file is generated correctly."""
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="txt")
    output_paths = builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)

    # The new code returns a list, so we pick the first
    assert isinstance(output_paths, list), "Expected a list of output paths"
    assert len(output_paths) == 1, "Should only have 1 output path with a single format"
    output_file = output_paths[0]

    assert os.path.exists(output_file), "Expected text output file to be created"
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "📂 Repository Structure Overview" in content
    assert "Mock content for testing." in content

def test_generate_json_output(clean_output_dir, mock_file_system):
    """Test if JSON output file is generated correctly."""
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="json")
    output_paths = builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)

    assert len(output_paths) == 1
    output_file = output_paths[0]

    assert os.path.exists(output_file), "Expected JSON output file to be created"
    with open(output_file, "r", encoding="utf-8") as f:
        json_data = json.load(f)
    
    assert "repository_structure" in json_data
    assert len(json_data["files"]) == len(MOCK_FILES)
    assert json_data["files"][0]["content"] == "Mock content for testing."

def test_handle_missing_files(clean_output_dir):
    """Ensure missing files are logged instead of causing failure."""
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="txt")
    missing_file = os.path.join(TEST_OUTPUT_DIR, "text", "missing_file.txt")

    output_paths = builder.generate_output([missing_file], TEST_OUTPUT_DIR)
    output_file = output_paths[0]

    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "[Error: File" in content

def test_max_lines_limited_output(clean_output_dir, mock_file_system):
    """Ensure that the --max-lines argument is enforced."""
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="txt", max_lines=1)
    output_paths = builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)
    output_file = output_paths[0]

    assert os.path.exists(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        content_lines = f.readlines()

    # Ensure that no file has more than one content line
    assert sum(1 for line in content_lines if "Mock content" in line) == len(MOCK_FILES)

def test_output_directory_structure():
    """Ensure that output directory structure is created correctly."""
    for subdir in ["text", "json", "md"]:
        assert os.path.exists(os.path.join(TEST_OUTPUT_DIR, subdir))

def test_generate_markdown_output(clean_output_dir, mock_file_system):
    """Test if Markdown output is correctly generated and contains expected content."""
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="md")
    output_paths = builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)
    output_file = output_paths[0]

    assert os.path.exists(output_file), f"❌ Markdown output file {output_file} was not created!"

    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "# 📂 Repository Overview:" in content, "❌ Repository name header missing!"
    assert "## 📜 Folder Structure" in content, "❌ Folder structure missing!"
    assert "### `file1.py`" in content, "❌ Expected file section missing!"
    assert "### `file2.md`" in content, "❌ Expected file section missing!"
    assert "Mock content for testing." in content, "❌ Extracted file content missing!"

    print(f"✅ Markdown output test passed! File: {output_file}")

def test_multi_format_output(clean_output_dir, mock_file_system):
    """
    Test if multiple output formats are generated in one call (e.g. "txt,json").
    """
    builder = OutputBuilder(TEST_REPO_NAME, output_dir=TEST_OUTPUT_DIR, output_format="txt,json")
    output_paths = builder.generate_output(list(mock_file_system.iterdir()), mock_file_system)

    # We expect 2 output paths
    assert len(output_paths) == 2, "Should generate 2 files for 'txt,json' multi-format"

    text_path = os.path.join(TEST_OUTPUT_DIR, "text", f"{TEST_REPO_NAME}.txt")
    json_path = os.path.join(TEST_OUTPUT_DIR, "json", f"{TEST_REPO_NAME}.json")
    assert text_path in output_paths, "Expected the text file in the list"
    assert json_path in output_paths, "Expected the json file in the list"

    assert os.path.exists(text_path), "Text file wasn't created!"
    assert os.path.exists(json_path), "JSON file wasn't created!"
