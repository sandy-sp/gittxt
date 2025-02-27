import os
import json
import pytest
from gittxt.output_builder import OutputBuilder

# Define expected directory paths inside `src/gittxt-outputs/`
SRC_DIR = os.path.dirname(__file__)  # `tests/`
OUTPUT_DIR = os.path.join(SRC_DIR, "../src/gittxt-outputs")
TEXT_DIR = os.path.join(OUTPUT_DIR, "text")
JSON_DIR = os.path.join(OUTPUT_DIR, "json")

@pytest.fixture(scope="function")
def clean_output_dir():
    """Ensure the output directories are clean before each test."""
    for folder in [TEXT_DIR, JSON_DIR]:
        for file in os.listdir(folder):
            os.remove(os.path.join(folder, file))  # Remove only files, not folders

@pytest.fixture
def sample_files(tmp_path):
    """Create sample text files for testing."""
    file1 = tmp_path / "file1.py"
    file1.write_text("print('Hello from Python')\n")  # Ensure newline consistency

    file2 = tmp_path / "file2.txt"
    file2.write_text("Hello World in text file\n")

    return [str(file1), str(file2)], str(tmp_path)

def test_generate_json_output(clean_output_dir, sample_files):
    """Test generating a `.json` output file."""
    files, repo_path = sample_files
    builder = OutputBuilder(repo_name="test_repo", output_format="json")
    output_file = builder.generate_output(files, repo_path)

    assert os.path.exists(output_file), "JSON output file was not created"
    assert output_file.endswith(".json"), "Output file does not have .json extension"

    with open(output_file, "r") as f:
        data = json.load(f)
        assert "repository_structure" in data, "Tree structure missing from JSON output"
        assert len(data["files"]) == 2, "Incorrect number of files in JSON output"
        assert data["files"][0]["content"].strip() == "print('Hello from Python')", "Python file content incorrect"
        assert data["files"][1]["content"].strip() == "Hello World in text file", "Text file content incorrect"

def test_handle_missing_file(clean_output_dir, tmp_path):
    """Test handling of missing files without crashing."""
    missing_file = tmp_path / "missing.txt"
    files = [str(missing_file)]
    builder = OutputBuilder(repo_name="test_repo", output_format="txt")
    output_file = builder.generate_output(files, str(tmp_path))

    assert os.path.exists(output_file), "Output file should be created even if some files are missing"

    with open(output_file, "r") as f:
        content = f.read()
        assert "[Warning: Missing file" in content, "Missing file error was not logged properly"
