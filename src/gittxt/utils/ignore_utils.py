from gittxt.core.logger import Logger

logger = Logger.get_logger(__name__)


def parse_ignore_file(path):
    """
    Parse a .gittxtignore file, returning cleaned ignore patterns.
    Ignores lines that are empty or start with '#'.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        ]
    except Exception as e:
        logger.warning(f"⚠️ Failed to parse ignore file: {path} → {e}")
        return []
