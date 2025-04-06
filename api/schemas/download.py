from enum import Enum

class OutputFormat(str, Enum):
    txt = "txt"
    md = "md"
    json = "json"
    zip = "zip"
