from gittxt.utils.tree_utils import generate_tree

def test_tree_generation_basic(tmp_path):
    # Create mock directory tree
    (tmp_path / "src").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('ok')")
    (tmp_path / "docs" / "guide.md").write_text("# Guide")

    tree = generate_tree(tmp_path)

    assert "src" in tree
    assert "docs" in tree
    assert "main.py" in tree
    assert "guide.md" in tree


def test_tree_respects_max_depth(tmp_path):
    # Deep structure
    (tmp_path / "level1" / "level2" / "level3").mkdir(parents=True)
    (tmp_path / "level1" / "file1.py").write_text("print('1')")
    (tmp_path / "level1" / "level2" / "file2.py").write_text("print('2')")
    (tmp_path / "level1" / "level2" / "level3" / "file3.py").write_text("print('3')")

    tree = generate_tree(tmp_path, max_depth=1)

    assert "file1.py" in tree
    assert "level2" in tree
    assert "file2.py" not in tree  # too deep


def test_tree_respects_exclude_dirs(tmp_path):
    # Setup .git folder to exclude
    (tmp_path / ".git").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('ok')")

    tree = generate_tree(tmp_path)
    assert ".git" not in tree
    assert "src" in tree
    assert "main.py" in tree
