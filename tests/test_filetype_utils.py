from gittxt.utils.filetype_utils import classify_simple, classify_file
from gittxt.config import FiletypeConfigManager

def test_classify_simple_textual_vs_non_textual(tmp_path):
    code_file = tmp_path / "main.py"
    docs_file = tmp_path / "README.md"
    image_file = tmp_path / "photo.png"
    binary_file = tmp_path / "custom_file.bin"

    code_file.write_text("print('hello')")
    docs_file.write_text("# Documentation")
    image_file.write_bytes(b"PNGDATA")
    binary_file.write_bytes(b"\x00\x01\x02")

    assert classify_simple(code_file)[0] == "TEXTUAL"
    assert classify_simple(docs_file)[0] == "TEXTUAL"
    assert classify_simple(image_file)[0] == "NON-TEXTUAL"
    assert classify_simple(binary_file)[0] == "NON-TEXTUAL"


def test_dynamic_whitelist_blacklist(tmp_path):
    whitelist_ext = ".customext"
    blacklist_ext = ".badext"

    # Dynamically add to config
    FiletypeConfigManager.add_to_whitelist(whitelist_ext)
    FiletypeConfigManager.add_to_blacklist(blacklist_ext)

    custom_file = tmp_path / f"data{whitelist_ext}"
    blacklisted_file = tmp_path / f"malware{blacklist_ext}"

    custom_file.write_text("whitelisted content")
    blacklisted_file.write_bytes(b"malware")

    assert classify_simple(custom_file) == ("TEXTUAL", "custom")
    assert classify_simple(blacklisted_file) == ("NON-TEXTUAL", "blacklisted")


def test_classify_file_wrapper(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("version: 1.0")

    label = classify_file(config_file)
    assert label in {"configs", "docs"}  # YAML defaults to configs
