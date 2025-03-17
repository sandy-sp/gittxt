import shutil
from pathlib import Path
from zipfile import ZipFile


def delete_directory(path: Path) -> None:
    """
    Recursively delete a directory.

    :param path: Path to directory.
    """
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
        print(f"🗑️ Deleted directory: {path}")


def zip_files(file_paths: list[Path], zip_dest: Path) -> Path:
    """
    Create a ZIP archive from a list of files.

    :param file_paths: List of Path objects to files.
    :param zip_dest: Destination Path for the ZIP file.
    :return: Path to the created ZIP file.
    """
    zip_dest.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_dest, "w") as zipf:
        for file in file_paths:
            arcname = file.name  # or relative to a base folder if needed
            zipf.write(file, arcname=arcname)
    print(f"📦 Created ZIP archive: {zip_dest}")
    return zip_dest


def cleanup_temp_folder(temp_dir: Path) -> None:
    """
    Delete a temporary directory (e.g., cloned repo temp folder).

    :param temp_dir: Path to temp directory.
    """
    delete_directory(temp_dir)


def cleanup_old_outputs(output_dir: Path) -> None:
    """
    Optional: Cleanup previous outputs (text/json/md folders) before running a new scan.

    :param output_dir: Path to output directory.
    """
    for subdir in ["text", "json", "md"]:
        delete_directory(output_dir / subdir)
