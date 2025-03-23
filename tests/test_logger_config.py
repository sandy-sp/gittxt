import logging
from gittxt.logger import Logger

def test_plain_logger_output(capsys):
    # Manually create isolated logger instance
    logger = logging.getLogger("plain-test")
    logger.setLevel(logging.INFO)

    # Clear any pre-existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create a StreamHandler tied to stdout
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.info("plain message")
    captured = capsys.readouterr()
    assert "plain message" in captured.err


def test_json_logger_output(monkeypatch, capsys):
    monkeypatch.setenv("GITTXT_LOG_FORMAT", "json")
    Logger.setup_logger()
    log = Logger.get_logger("json-test")
    log.warning("json output test")
    captured = capsys.readouterr()
    assert '{"level": "WARNING"' in captured.err

def test_rotating_file_handler_creates_log(tmp_path, monkeypatch):
    monkeypatch.setenv("GITTXT_LOG_FORMAT", "plain")
    monkeypatch.setenv("GITTXT_LOGGING_LEVEL", "DEBUG")

    # Override log directory
    monkeypatch.setattr(Logger, "LOG_DIR", tmp_path)
    monkeypatch.setattr(Logger, "LOG_FILE", tmp_path / "gittxt.log")

    Logger.setup_logger()
    log = Logger.get_logger("file-test")
    log.debug("file logger works")

    # Confirm log file created
    log_path = tmp_path / "gittxt.log"
    assert log_path.exists()
    content = log_path.read_text()
    assert "file logger works" in content
