import pytest
import logging
from src.common.logging.logger_config import setup_logger

def test_setup_logger():
    logger = setup_logger("fastlangframe.test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "fastlangframe.test_logger"
    assert len(logger.handlers) >= 1
