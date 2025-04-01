import os
import json
from .config import API_TMP_DIR

def get_output_file(scan_id: str, fmt: str) -> str:
    base = os.path.join(API_TMP_DIR, scan_id)
    if fmt == "zip":
        return os.path.join(base, "archive.zip")
    return os.path.join(base, "outputs", f"repo.{fmt}")

def load_summary_data(scan_id: str) -> dict:
    summary_path = os.path.join(API_TMP_DIR, scan_id, "outputs", "summary.json")
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
