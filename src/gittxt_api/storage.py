import os
from .config import API_TMP_DIR

def get_output_file(scan_id: str, fmt: str) -> str:
    base = os.path.join(API_TMP_DIR, scan_id)
    if fmt == "zip":
        return os.path.join(base, "archive.zip")
    return os.path.join(base, "outputs", f"repo.{fmt}")
