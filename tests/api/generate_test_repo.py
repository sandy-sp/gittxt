from pathlib import Path
import zipfile
import shutil


def generate_test_repo(base_dir="tests/api/test_repo"):
    base = Path(base_dir).resolve()
    base.mkdir(parents=True, exist_ok=True)

    # ─── Textual Files ─────────────────────
    (base / "README.md").write_text(
        "# Sample README\nThis is a test file.\n", encoding="utf-8"
    )
    (base / "script.py").write_text("print('Hello, world!')\n", encoding="utf-8")
    (base / "included.txt").write_text(
        "This file should be included by include pattern.\n", encoding="utf-8"
    )
    (base / "script.min.js").write_text("var a=1;" * 5000, encoding="utf-8")  # Minified

    # ─── Large File (>5MB) ─────────────────
    large_file = base / "script_large.py"
    with open(large_file, "w", encoding="utf-8") as f:
        f.write("x = 'abc123'\n" * (1024 * 600))  # ~6MB

    # ─── Non-Textual Files ─────────────────
    (base / "binary.dat").write_bytes(b"\x00\x01\x02\x03")
    (base / "archive.zip").write_bytes(b"PK\x03\x04")
    (base / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    # ─── Text Without Extension ────────────
    (base / "no_extension").write_text(
        "No extension but still text.\n", encoding="utf-8"
    )
    (base / ".hidden").write_text("Hidden file.\n", encoding="utf-8")
    (base / "data.csv").write_text("id,name\n1,Alice\n2,Bob\n", encoding="utf-8")

    # ─── .gittxtignore File ────────────────
    (base / ".gittxtignore").write_text(
        "node_modules/\n*.zip\nscript_large.py\n", encoding="utf-8"
    )

    # ─── Ignored Directories ───────────────
    (base / "node_modules").mkdir(parents=True, exist_ok=True)
    (base / "node_modules/lib.js").write_text(
        "console.log('should be excluded');", encoding="utf-8"
    )

    (base / "dist").mkdir(parents=True, exist_ok=True)
    (base / "dist/bundle.js").write_text("// built file\n", encoding="utf-8")

    # ─── Nested Directories ────────────────
    subdir = base / "subdir"
    subdir.mkdir(exist_ok=True)
    (subdir / "nested.txt").write_text("Nested file content\n", encoding="utf-8")

    deep = subdir / "deep/very/deep"
    deep.mkdir(parents=True, exist_ok=True)
    (deep / "file.md").write_text("# Deep file\nSome deep content\n", encoding="utf-8")

    print(f"✅ Test repo created at: {base}")


def generate_test_zip():
    # Generate the test repository
    test_dir = Path("tests/api/test_repo")
    generate_test_repo(test_dir)

    zip_path = Path("tests/api/test_repo.zip")

    # Clean up existing zip file
    if zip_path.exists():
        zip_path.unlink()

    # Zip the test repository
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in test_dir.rglob("*"):
            zipf.write(file, arcname=file.relative_to(test_dir.parent))

    print(f"✅ Created {zip_path}")

    # Clean up the test repository folder
    shutil.rmtree(test_dir)
    print(f"✅ Deleted test repository folder: {test_dir}")


if __name__ == "__main__":
    generate_test_zip()
