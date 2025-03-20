import shutil
from pathlib import Path

def delete_directory(path: Path) -> None:
    """
    Recursively delete a directory.

    :param path: Path to directory.
    """
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
        print(f"🗑️ Deleted directory: {path}")


def cleanup_temp_folder(temp_dir: Path) -> None:
    """
    Delete a temporary directory (e.g., cloned repo temp folder).
    """
    delete_directory(temp_dir)


def cleanup_old_outputs(output_dir: Path) -> None:
    """
    Cleanup previous outputs (text/json/md folders) before running a new scan.
    """
    for subdir in ["text", "json", "md"]:
        delete_directory(output_dir / subdir)
