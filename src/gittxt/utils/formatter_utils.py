from gittxt.utils.filetype_utils import classify_simple

def sort_textual_files(files):
    priority = ["readme", "license", ".gitignore", "config", "docs", "code", "data"]
    def file_priority(file):
        fname = file.name.lower()
        if fname.startswith("readme"):
            return 0
        if fname in {"license", "notice"}:
            return 1
        if fname in {".gitignore", ".dockerignore", ".gitattributes"}:
            return 2
        ext_priority = {"configs": 3, "docs": 4, "code": 5, "data": 6}
        _, subcat = classify_simple(file)
        return ext_priority.get(subcat, 7)
    return sorted(files, key=file_priority)
