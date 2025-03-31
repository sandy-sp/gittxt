import shutil
from pathlib import Path
from gittxt.core.constants import OUTPUT_SUBDIRS
from gittxt.core.logger import Logger

logger = Logger.get_logger(__name__)

def delete_directory(path: Path) -> None:
    if path.exists() and path.is_dir():
        try:
            shutil.rmtree(path)
            logger.info(f"🗑️ Deleted directory: {path}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to delete {path}: {e}")

def cleanup_temp_folder(temp_dir: Path) -> None:
    """
    Delete a temporary directory (e.g., cloned repo temp folder).
    """
    delete_directory(temp_dir)


def cleanup_old_outputs(output_dir: Path) -> None:
    """
    Cleanup previous outputs before running a new scan, including ZIPs and temp folders.
    """
    for subdir in OUTPUT_SUBDIRS:
        delete_directory(output_dir / subdir)
