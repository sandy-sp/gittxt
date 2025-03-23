from gittxt.logger import Logger

def test_plain_logger_output(monkeypatch, capsys):
    # Force plain logging to stdout during this test
    monkeypatch.setenv("GITTXT_LOG_FORMAT", "plain")
    Logger.setup_logger(force_stdout=True)

    log = Logger.get_logger("plain-test")
    log.info("plain message")

    captured = capsys.readouterr()
    assert "plain message" in captured.out


def test_json_logger_output(monkeypatch, capsys):
    # Force json mode
    monkeypatch.setenv("GITTXT_LOG_FORMAT", "json")
    Logger.setup_logger()
    log = Logger.get_logger("json-test")
    log.warning("json output test")
    captured = capsys.readouterr()
    assert '{"level": "WARNING"' in captured.out


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
