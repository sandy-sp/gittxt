import pytest
from pathlib import Path
from gittxt.utils.formatter_utils import sort_textual_files

@pytest.mark.asyncio
async def test_sort_textual_files_readme_first(tmp_path):
    # Arrange
    root = tmp_path / "repo"
    root.mkdir()

    # Files to simulate repo content
    readme = root / "README.md"
    config = root / "config.yaml"
    main = root / "src" / "main.py"
    nested = root / "docs" / "guide.txt"

    # Create file paths
    (root / "src").mkdir()
    (root / "docs").mkdir()
    readme.write_text("# README")
    config.write_text("version: 1.0")
    main.write_text("print('hello')")
    nested.write_text("usage instructions")

    # Unordered input
    input_files = [main, config, nested, readme]

    # Act
    result = sort_textual_files(input_files, base_path=root)

    # Assert
    assert result[0].name.lower().startswith("readme")
    assert result[1:] == sorted(result[1:], key=lambda f: f.relative_to(root).as_posix().lower())
