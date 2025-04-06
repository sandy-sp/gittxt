from gittxt.core.scanner import scan_repo
from gittxt.core.output_builder import build_outputs

def run_gittxt_scan(repo_url: str, options: dict):
    scan_result = scan_repo(repo_url, **options)
    return build_outputs(scan_result, **options)
