import logging
from utils.logging_utils import setup_logging


def test_setup_logging_returns_logger():
    logger = setup_logging("DEBUG")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "tokenembed"
    assert logger.getEffectiveLevel() == logging.DEBUG

def test_setup_logging_default_level():
    logger = setup_logging()
    assert logger.getEffectiveLevel() == logging.INFO


def test_setup_logging_with_file(tmp_path):
    log_file = tmp_path / "test.log"
    logger = setup_logging("WARNING", str(log_file))

    logger.warning("This is a test warning")
    logger.debug("This debug should not be logged")

    with open(log_file) as f:
        content = f.read()

    assert "This is a test warning" in content
    assert "debug" not in content
