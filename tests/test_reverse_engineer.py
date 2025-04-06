import os
import json
import pytest
import zipfile
from pathlib import Path
from unittest.mock import patch

from gittxt.core.reverse_engineer import reverse_from_report


@pytest.mark.asyncio
async def test_reverse_from_txt_report(tmp_path):
    """Test reconstruction from a .txt report file"""
    # Arrange
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    
    # Create a mock txt report
    txt_report = report_dir / "sample_repo.txt"
    txt_content = """
    # Repository: sample_repo
    
    ## File: README.md
    
    ```
    # Sample Repo
    This is a sample repository for testing.
    ```
    
    ## File: src/main.py
    
    ```python
    def hello():
        return "Hello, world!"
        
    if __name__ == "__main__":
        print(hello())
    ```
    """
    txt_report.write_text(txt_content)
    
    # Act
    with patch('gittxt.core.reverse_engineer.get_output_dir', return_value=str(tmp_path / "output")):
        zip_path = reverse_from_report(str(txt_report))
    
    # Assert
    assert os.path.exists(zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        file_list = zf.namelist()
        assert "README.md" in file_list
        assert "src/main.py" in file_list
        
        # Check content
        assert "Sample Repo" in zf.read("README.md").decode('utf-8')
        assert "def hello():" in zf.read("src/main.py").decode('utf-8')


@pytest.mark.asyncio
async def test_reverse_from_json_report(tmp_path):
    """Test reconstruction from a .json report file"""
    # Arrange
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    
    # Create a mock json report
    json_report = report_dir / "sample_repo.json"
    json_data = {
        "repository": "sample_repo",
        "files": [
            {
                "path": "README.md",
                "content": "# Sample Repo\nThis is a sample repository for testing."
            },
            {
                "path": "src/main.py",
                "content": "def hello():\n    return \"Hello, world!\"\n\nif __name__ == \"__main__\":\n    print(hello())"
            }
        ]
    }
    json_report.write_text(json.dumps(json_data))
    
    # Act
    with patch('gittxt.core.reverse_engineer.get_output_dir', return_value=str(tmp_path / "output")):
        zip_path = reverse_from_report(str(json_report))
    
    # Assert
    assert os.path.exists(zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        file_list = zf.namelist()
        assert "README.md" in file_list
        assert "src/main.py" in file_list


@pytest.mark.asyncio
async def test_reverse_from_md_report(tmp_path):
    """Test reconstruction from a .md report file"""
    # Arrange
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    
    # Create a mock markdown report
    md_report = report_dir / "sample_repo.md"
    md_content = """
    # Repository: sample_repo
    
    ## File: README.md
    
    ```markdown
    # Sample Repo
    This is a sample repository for testing.
    ```
    
    ## File: src/main.py
    
    ```python
    def hello():
        return "Hello, world!"
        
    if __name__ == "__main__":
        print(hello())
    ```
    """
    md_report.write_text(md_content)
    
    # Act
    with patch('gittxt.core.reverse_engineer.get_output_dir', return_value=str(tmp_path / "output")):
        zip_path = reverse_from_report(str(md_report))
    
    # Assert
    assert os.path.exists(zip_path)
    with zipfile.ZipFile(zip_path) as zf:
        file_list = zf.namelist()
        assert "README.md" in file_list
        assert "src/main.py" in file_list


@pytest.mark.asyncio
async def test_invalid_report_format(tmp_path):
    """Test handling of unsupported report formats"""
    # Arrange
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    
    # Create an invalid report file
    invalid_report = report_dir / "sample_repo.csv"
    invalid_report.write_text("This is not a supported format")
    
    # Act & Assert
    with pytest.raises(ValueError):
        reverse_from_report(str(invalid_report))


@pytest.mark.asyncio
async def test_malformed_report_content(tmp_path):
    """Test handling of malformed report content"""
    # Arrange
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    
    # Create a malformed json report
    bad_json = report_dir / "malformed.json"
    bad_json.write_text("{not valid json")
    
    # Act & Assert
    with pytest.raises(Exception):
        reverse_from_report(str(bad_json))
