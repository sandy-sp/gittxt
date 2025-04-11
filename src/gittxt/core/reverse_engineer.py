import os
import json
import zipfile
import tempfile
import shutil
import re
from datetime import datetime
from pathlib import Path
from gittxt.core.constants import REVERSE_DIR
from gittxt.core.logger import Logger

logger = Logger.get_logger(__name__)


def reverse_from_report(report_path: str, output_dir: Path = None) -> str:
    if output_dir is None:
        from gittxt import OUTPUT_REVERSE_DIR
        output_dir = OUTPUT_REVERSE_DIR
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(report_path).suffix.lower()

    if ext == ".json":
        files = parse_json_auto(report_path)
    elif ext == ".txt":
        files = parse_text_auto(report_path)
    elif ext == ".md":
        files = parse_md_auto(report_path)
    else:
        raise ValueError("Unsupported report format. Use .txt, .md, or .json")

    if not files:
        raise ValueError("No reconstructable files found in the report.")

    repo_name = infer_repo_name(files)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    with tempfile.TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir) / repo_name
        root_dir.mkdir(parents=True, exist_ok=True)

        for rel_path, content in files.items():
            abs_path = root_dir / rel_path
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(content, encoding='utf-8')

        zip_filename = f"{repo_name}_reconstructed_{timestamp}.zip"
        zip_path = output_dir / zip_filename
        shutil.make_archive(str(zip_path.with_suffix("")), 'zip', root_dir)
        logger.info(f"📦 Reconstructed repository written to: {zip_path}")
        return str(zip_path)


# -------------------------------
# === Format Auto-Detectors ===
# -------------------------------

def parse_json_auto(report_path: str) -> dict:
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    files = {}
    entries = data.get("files", [])

    for entry in entries:
        path = entry.get("path")
        content = entry.get("content")
        if not path or content is None:
            continue
        files[path] = content.strip("\n")

    return files


def parse_text_auto(report_path: str) -> dict:
    files = {}
    current_path = None
    content_lines = []

    lite_pattern = re.compile(r"^---> File: (.+?) <---$")
    rich_pattern = re.compile(r"^---> FILE: (.+?) \| TYPE: .+? \| SIZE: .+? \| TOKENS: .+? <---$")

    with open(report_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            match_lite = lite_pattern.match(stripped)
            match_rich = rich_pattern.match(stripped)

            if match_lite or match_rich:
                if current_path and content_lines:
                    files[current_path] = "\n".join(content_lines).strip()
                current_path = match_lite.group(1) if match_lite else match_rich.group(1)
                content_lines = []
            else:
                if current_path:
                    content_lines.append(line.rstrip())

    if current_path and content_lines:
        files[current_path] = "\n".join(content_lines).strip()

    return files


def parse_md_auto(report_path: str) -> dict:
    files = {}
    current_path = None
    inside_code = False
    content_lines = []

    file_header_pattern = re.compile(r'^### (?:File: )?`(.+?)`$')

    with open(report_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            header_match = file_header_pattern.match(line)

            if header_match:
                if current_path and content_lines:
                    files[current_path] = "\n".join(content_lines).strip()
                current_path = header_match.group(1)
                content_lines = []
                inside_code = False
                continue

            if line.strip() == "```text":
                inside_code = True
                continue
            elif line.strip() == "```" and inside_code:
                inside_code = False
                continue

            if inside_code and current_path:
                content_lines.append(line)

    if current_path and content_lines:
        files[current_path] = "\n".join(content_lines).strip()

    return files


# -------------------------------
# === Repo Name Guessing ===
# -------------------------------

def infer_repo_name(files: dict) -> str:
    top_dirs = [Path(p).parts[0] for p in files.keys() if "/" in p]
    if top_dirs:
        return top_dirs[0]
    return "reconstructed_repo"
