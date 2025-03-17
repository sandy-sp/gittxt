from pathlib import Path
import mimetypes
from binaryornot.check import is_binary

# ----------- Classification Logic -----------

def is_text_file(file: Path) -> bool:
    """
    Detects if the file is a readable text file using binary detection + MIME fallback.
    """
    try:
        if file.is_dir():
            return False
        if not file.exists():
            return False
        if not file.is_file():
            return False
        return not is_binary(str(file))
    except Exception:
        return False

def get_mime_type(file: Path) -> str:
    """
    Returns the MIME type of the file, defaults to 'application/octet-stream'.
    """
    mime_type, _ = mimetypes.guess_type(str(file))
    return mime_type or 'application/octet-stream'

def is_code_file(file: Path) -> bool:
    code_extensions = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".rb", ".php", ".sh"}
    return file.suffix.lower() in code_extensions

def is_doc_file(file: Path) -> bool:
    doc_extensions = {".md", ".rst", ".txt", ".adoc"}
    return file.suffix.lower() in doc_extensions or file.name.lower().startswith("readme")

def is_image_file(file: Path) -> bool:
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".svg"}
    return file.suffix.lower() in image_extensions

def is_csv_or_data_file(file: Path) -> bool:
    data_extensions = {".csv", ".json", ".yaml", ".yml"}
    return file.suffix.lower() in data_extensions

def is_media_file(file: Path) -> bool:
    media_extensions = {".mp4", ".avi", ".mov", ".wav", ".mp3"}
    return file.suffix.lower() in media_extensions

# ----------- Main Classifier -----------

def classify_file(file: Path) -> str:
    """
    Classify a file into:
    - code: Source code files (.py, .js, etc.)
    - doc: Documentation (.md, .txt, .rst)
    - image: Images (png, jpg, svg, etc.)
    - csv: CSV / JSON / YAML data
    - media: Video or audio
    - text: Miscellaneous text files
    - other: Binary or unsupported formats
    """
    if not file.exists() or not file.is_file():
        return "other"

    if is_code_file(file):
        return "code"
    if is_doc_file(file):
        return "docs"
    if is_image_file(file):
        return "image"
    if is_csv_or_data_file(file):
        return "csv"
    if is_media_file(file):
        return "media"
    if is_text_file(file):
        return "text"

    return "other"

