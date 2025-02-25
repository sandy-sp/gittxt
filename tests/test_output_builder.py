import os
import json
import pytest
from gittxt.output_builder import OutputBuilder

@pytest.fixture
def sample_files(tmp_path):
    """Create sample text files for testing."""
    file1 = tmp_path / "file1.py"
    file1.write_text("print('Hello')")

    file2 = tmp_path / "file2.txt"
    file2.write_text("Hello World")

    return [str(file1), str(file2)]

def test_generate_text_output(sample_files, tmp_path):
    """Test generating a text output file."""
    output_file = tmp_path / "output.txt"
    builder = OutputBuilder(output_file=str(output_file))
    builder.generate_output(sample_files)

    assert output_file.exists()
    assert "=== File:" in output_file.read_text()  # Check header format

def test_generate_json_output(sample_files, tmp_path):
    """Test generating a JSON output file."""
    output_file = tmp_path / "output.json"
    builder = OutputBuilder(output_file=str(output_file), output_format="json")
    builder.generate_output(sample_files)

    assert output_file.exists()
    
    with open(output_file, "r") as f:
        data = json.load(f)
        assert isinstance(data, list)
        assert "file" in data[0]
        assert "content" in data[0]
