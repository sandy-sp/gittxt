import os

def sanitize_filename(filename):
    """Remove invalid characters from filenames."""
    return "".join(c for c in filename if c.isalnum() or c in (" ", ".", "_")).rstrip()
