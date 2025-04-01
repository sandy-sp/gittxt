import uuid

def generate_scan_id() -> str:
    return str(uuid.uuid4())
