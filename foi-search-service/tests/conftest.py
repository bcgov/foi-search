import pytest
from config import reset_config, get_config
from utils.logging_utils import setup_logging

@pytest.fixture(autouse=True, scope="session")
def test_config():
    reset_config()
    get_config(".env.test")

@pytest.fixture(autouse=True, scope="session")
def setup_test_logging():
    # Logging uses test config, runs once per test session
    setup_logging(
        log_level=get_config().global_config.log_level,
        log_file=get_config().global_config.log_file
    )