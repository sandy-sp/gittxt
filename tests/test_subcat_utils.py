import pytest
from pathlib import Path
from gittxt.utils.subcat_utils import infer_textual_subcategory

@pytest.mark.parametrize("name,content,expected", [
    ("main.py", "def hello():\n  pass", "code"),
    ("index.js", "import fs from 'fs'", "code"),
    ("config.yaml", "setting: true\nparameter: value", "config"),
    ("data.csv", "id,value\n1,2", "data"),
    ("LICENSE", "MIT License", "meta"),
    ("notes.txt", "this is plain text", "other"),
])
def test_infer_textual_subcategory(name, content, expected, tmp_path):
    file = tmp_path / name
    file.write_text(content)
    result = infer_textual_subcategory(file, content)
    assert result == expected
