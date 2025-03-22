from gittxt.utils.summary_utils import generate_summary

def test_summary_counts_and_breakdown(tmp_path):
    # Create a mock repo structure
    code_file = tmp_path / "main.py"
    docs_file = tmp_path / "README.md"
    data_file = tmp_path / "data.csv"
    binary_file = tmp_path / "file.bin"

    code_file.write_text("print('hello world')")
    docs_file.write_text("# Documentation")
    data_file.write_text("id,value\n1,100\n")
    binary_file.write_bytes(b"\x00\x01\x02\x03")

    summary = generate_summary([code_file, docs_file, data_file, binary_file])

    assert summary["total_files"] == 4
    assert summary["total_size"] > 0
    assert summary["file_type_breakdown"]["code"] == 1
    assert summary["file_type_breakdown"]["docs"] == 1
    assert summary["file_type_breakdown"]["data"] == 1
    assert summary["file_type_breakdown"]["binary"] == 1


def test_token_fallback_when_tiktoken_missing(monkeypatch, tmp_path):
    # Create a simple text file
    text_file = tmp_path / "note.txt"
    text_file.write_text("token fallback test " * 10)

    # Simulate tiktoken failure by patching estimate_tokens_from_file
    from gittxt.utils import summary_utils
    monkeypatch.setattr(summary_utils, "estimate_tokens_from_file", lambda f, encoding_name=None: 50)

    summary = generate_summary([text_file])
    assert summary["estimated_tokens"] == 50
    assert summary["tokens_by_type"]["docs"] == 50
