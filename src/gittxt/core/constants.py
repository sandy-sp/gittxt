TEXT_DIR = "text"
JSON_DIR = "json"
MD_DIR = "md"
ZIP_DIR = "zips"
TEMP_DIR = "temp"

# Potentially store default excludes in a single place, if you don’t want them in config.json
EXCLUDED_DIRS_DEFAULT = [
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "env",
    ".mypy_cache",
    ".pytest_cache",
    ".vscode",
    ".idea",
]

# If you want a quick reference to all subdirectories that might be cleaned:
OUTPUT_SUBDIRS = [TEXT_DIR, JSON_DIR, MD_DIR, ZIP_DIR, TEMP_DIR]

# Updated config keys to textual_exts / non_textual_exts
DEFAULT_FILETYPE_CONFIG = {
    "textual_exts": [".py", ".md", ".txt", ".html", ".json", ".yml", ".yaml", ".csv"],
    "non_textual_exts": [".zip", ".exe", ".bin", ".docx", ".xls", ".pdf"],
}

# Keys used in config filters
VALID_KEYS = {"excluded_dirs", "textual_exts", "non_textual_exts"}