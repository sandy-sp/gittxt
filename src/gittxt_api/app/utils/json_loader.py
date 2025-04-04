import json
import os


def load_json(path: str):
    if not os.path.exists(path):
        print(f"[WARN] JSON file not found: {path}")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load JSON from {path}: {e}")
        return {}
