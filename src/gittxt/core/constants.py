TEXT_DIR = "text"
JSON_DIR = "json"
MD_DIR = "md"
ZIP_DIR = "zips"
TEMP_DIR = "temp"

# Potentially store default excludes in a single place, if you don’t want them in config.json
DEFAULT_EXCLUDE_DIRS = [
    ".git", 
    "__pycache__", 
    "node_modules", 
    ".vscode", 
    ".pytest_cache"
]

# If you want a quick reference to all subdirectories that might be cleaned:
OUTPUT_SUBDIRS = [TEXT_DIR, JSON_DIR, MD_DIR, ZIP_DIR, TEMP_DIR]
