import os
import json
import zipfile
import tempfile
import shutil
import re

from pathlib import Path

def reverse_from_report(report_path: str) -> str:
    ext = Path(report_path).suffix.lower()
    
    if ext == ".json":
        files = parse_json_report(report_path)
    elif ext in ".txt":
        files = parse_textual_report(report_path)
    elif ext == ".md":
        files = parse_markdown_report(report_path)

    else:
        raise ValueError("Unsupported report format. Use .json, .txt, or .md")

    if not files:
        raise ValueError("No files found in the report.")

    # Infer top-level folder name (e.g., repo name)
    repo_name = infer_repo_name(files)

    with tempfile.TemporaryDirectory() as temp_dir:
        root_dir = Path(temp_dir) / repo_name
        root_dir.mkdir(parents=True, exist_ok=True)

        for rel_path, content in files.items():
            abs_path = root_dir / rel_path
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(content, encoding='utf-8')

        # Create ZIP file in cwd
        zip_filename = f"{repo_name}_reconstructed.zip"
        zip_path = Path.cwd() / zip_filename
        shutil.make_archive(zip_path.with_suffix(""), 'zip', root_dir)

        return str(zip_path)

def parse_json_report(report_path: str) -> dict:
    """
    Parses a Gittxt JSON report (lite or rich) and extracts file paths and contents.

    Returns:
        dict: { "path/to/file.py": "file content" }
    """
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "files" not in data:
        raise ValueError("Invalid Gittxt JSON report: missing 'files' section")

    files = {}
    for entry in data["files"]:
        path = entry.get("path")
        content = entry.get("content")

        if not path or content is None:
            continue  # skip malformed or empty content

        files[path] = content.strip()

    return files


def parse_textual_report(report_path: str) -> dict:
    """
    Parses a Gittxt .txt or .md report and extracts file paths and content blocks.

    Returns:
        dict: { "path/to/file.py": "file content" }
    """
    files = {}
    current_path = None
    content_lines = []

    # Patterns for both lite and rich headers
    file_header_pattern = re.compile(
        r"^---> (?:FILE|File): (.+?) (?:<---|(?:\|.*<---))$"
    )

    with open(report_path, "r", encoding="utf-8") as f:
        for line in f:
            match = file_header_pattern.match(line.strip())
            if match:
                # Save previous file before starting new one
                if current_path and content_lines:
                    files[current_path] = "\n".join(content_lines).strip()
                current_path = match.group(1).strip()
                content_lines = []
            else:
                if current_path:
                    content_lines.append(line.rstrip())

    # Save last file
    if current_path and content_lines:
        files[current_path] = "\n".join(content_lines).strip()

    return files


def parse_markdown_report(report_path: str) -> dict:
    """
    Parses a Gittxt Markdown (.md) report and extracts file paths and contents.

    Returns:
        dict: { "path/to/file.py": "file content" }
    """
    files = {}
    current_path = None
    inside_code_block = False
    content_lines = []

    path_pattern = re.compile(r'^### (?:File: )?`(.+?)`')

    with open(report_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            # Detect start of a new file section
            match = path_pattern.match(line)
            if match:
                if current_path and content_lines:
                    files[current_path] = "\n".join(content_lines).strip()
                current_path = match.group(1).strip()
                content_lines = []
                inside_code_block = False
                continue

            # Detect start or end of code block
            if line.strip() == "```text":
                inside_code_block = True
                continue
            elif line.strip() == "```" and inside_code_block:
                inside_code_block = False
                continue

            # Accumulate lines inside code block
            if inside_code_block and current_path:
                content_lines.append(line)

    # Save final file
    if current_path and content_lines:
        files[current_path] = "\n".join(content_lines).strip()

    return files

def infer_repo_name(files: dict) -> str:
    # Return first-level folder or default name
    top_dirs = [Path(f).parts[0] for f in files.keys() if "/" in f]
    return top_dirs[0] if top_dirs else "reconstructed_repo"
