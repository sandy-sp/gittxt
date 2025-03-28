import os
from pathlib import Path

def generate_test_repo(base_dir="tests/test_repo"):
    base = Path(base_dir)
    base.mkdir(parents=True, exist_ok=True)

    # Simple textual files
    (base / "README.md").write_text("# Sample README\nThis is a test file.\n")
    (base / "script.py").write_text("print('Hello, world')\n")
    (base / "included.txt").write_text("This file should be included by include pattern.\n")
    (base / "script.min.js").write_text("var a=1;" * 5000)  # simulate minified js

    # Large file (5+ MB)
    large_file = base / "script_large.py"
    with open(large_file, "w") as f:
        f.write("x = 'abc123'\n" * (1024 * 600))  # ~6MB

    # Non-textual / binary / excluded
    (base / "binary.dat").write_bytes(b"\x00\x01\x02\x03")
    (base / "archive.zip").write_bytes(b"PK\x03\x04")
    (base / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (base / "no_extension").write_text("No extension but still text.\n")
    (base / ".hidden").write_text("Hidden file.\n")
    (base / "data.csv").write_text("id,name\n1,Alice\n2,Bob\n")

    # Exclude patterns via .gittxtignore
    (base / ".gittxtignore").write_text("node_modules/\n*.zip\nscript_large.py\n")

    # Ignored directories
    (base / "node_modules").mkdir(parents=True, exist_ok=True)
    (base / "node_modules/lib.js").write_text("console.log('should be excluded');\n")

    (base / "dist").mkdir(parents=True, exist_ok=True)
    (base / "dist/bundle.js").write_text("// built file\n")

    # Subdirectories with nested file
    subdir = base / "subdir"
    subdir.mkdir(exist_ok=True)
    (subdir / "nested.txt").write_text("Nested file content\n")

    deep = subdir / "deep/very/deep"
    deep.mkdir(parents=True, exist_ok=True)
    (deep / "file.md").write_text("# Deep file\nSome deep content\n")

    print(f"✅ Test repo created at: {base.resolve()}")

if __name__ == "__main__":
    generate_test_repo()
