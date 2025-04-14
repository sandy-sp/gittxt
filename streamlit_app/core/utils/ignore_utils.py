from pathlib import Path
from core.core.logger import Logger

logger = Logger.get_logger(__name__)


def parse_ignore_file(path: Path) -> list[str]:
    """
    Parse a .gittxtignore file and return a list of valid glob patterns.

    - Ignores blank lines and comments.
    - Expands directory patterns like 'node_modules/' into 'node_modules/*'.
    """
    try:
        patterns = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.endswith("/"):
                patterns.append(f"{line}*")
            else:
                patterns.append(line)
        return patterns
    except Exception as e:
        logger.warning(f"⚠️ Failed to parse ignore file: {path} → {e}")
        return []
