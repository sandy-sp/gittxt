from src.gittxt_api.utils import generate_scan_id

def test_generate_scan_id():
    scan_id = generate_scan_id()
    assert isinstance(scan_id, str)
    assert len(scan_id) > 0
