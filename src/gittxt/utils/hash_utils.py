from pathlib import Path
import hashlib

def get_file_hash(file_path: Path, algo: str = "sha256") -> str:
    """
    Generate a hash for a file using the specified hashing algorithm.
    Returns None if hashing fails.
    """
    hashers = {"sha256": hashlib.sha256, "md5": hashlib.md5}

    hasher = hashers.get(algo.lower())
    if not hasher:
        raise ValueError("Unsupported hash algorithm. Choose 'sha256' or 'md5'.")

    try:
        h = hasher()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None
