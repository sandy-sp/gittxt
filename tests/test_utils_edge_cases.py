from gittxt.utils import pattern_utils, tree_utils, hash_utils
from pathlib import Path
import tempfile

def test_pattern_utils_include_exclude():
    path = Path("/myrepo/src/example.py")
    assert pattern_utils.match_include(path, ["*.py"])
    assert not pattern_utils.match_include(path, ["*.md"])

    assert pattern_utils.match_exclude(path, ["src/*"])
    assert not pattern_utils.match_exclude(path, ["docs/*"])


def test_normalize_patterns():
    raw = [" .PY  ", " .md"]
    normalized = pattern_utils.normalize_patterns(raw)
    assert normalized == [".py", ".md"]


def test_tree_utils_depth(tmp_path):
    # Create nested folders
    (tmp_path / "level1" / "level2").mkdir(parents=True)
    (tmp_path / "level1" / "level2" / "file.txt").write_text("data")
    tree = tree_utils.generate_tree(tmp_path, max_depth=1)
    assert "level1" in tree
    assert "level2" not in tree  # max_depth=1 hides deeper


def test_hash_utils():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        tf.write(b"hash me")
        tf_path = Path(tf.name)

    md5_hash = hash_utils.get_file_hash(tf_path, algo="md5")
    sha256_hash = hash_utils.get_file_hash(tf_path, algo="sha256")

    assert len(md5_hash) == 32
    assert len(sha256_hash) == 64

    tf_path.unlink()

from gittxt.utils.filetype_utils import pipeline_classify, update_whitelist, update_blacklist

def test_pipeline_classify_with_overrides(tmp_path):
    # Simulate a .foo file
    dummy_file = tmp_path / "sample.foo"
    dummy_file.write_text("dummy")

    # Initially fallback to asset
    assert pipeline_classify(dummy_file) == "asset"

    # Whitelist it
    update_whitelist(".foo")
    assert pipeline_classify(dummy_file) == "docs"

    # Blacklist it again
    update_blacklist(".foo")
    assert pipeline_classify(dummy_file) == "asset"
