from pathlib import Path
import hashlib
from gittxt.core.logger import Logger

logger = Logger.get_logger(__name__)


def get_file_hash(file_path: Path, algo: str = "sha256") -> str:
    """
    Generate a hash for a file using the specified hashing algorithm.
    Returns None if hashing fails.
    """
    hashers = {
        "sha256": hashlib.sha256,
        "md5": hashlib.md5,
    }

    hasher_func = hashers.get(algo.lower())
    if not hasher_func:
        raise ValueError("Unsupported hash algorithm. Choose 'sha256' or 'md5'.")

    try:
        h = hasher_func()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception as e:
        logger.warning(f"⚠️ Failed to hash file {file_path}: {e}")
        return None
