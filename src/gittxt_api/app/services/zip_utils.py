import os
from typing import Dict


def generate_download_links(scan_id: str, formats: list, zip_enabled: bool) -> Dict[str, str]:
    base_url = f"/download/{scan_id}"

    links = {}
    for fmt in formats:
        links[fmt] = f"{base_url}/output.{fmt}"

    if zip_enabled:
        links["zip"] = f"{base_url}/bundle.zip"

    return links
