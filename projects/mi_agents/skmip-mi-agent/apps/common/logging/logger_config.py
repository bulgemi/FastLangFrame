import sys
from loguru import logger

logger.remove()

logger.add(
    sys.stdout,
    level="DEBUG",
    filter=lambda record: record["level"].name == "DEBUG",
    colorize=True,
    format="<green>[{time:HH:mm:ss}]</green> <cyan>{level}</cyan>: {message}",
)

logger.add(
    sys.stdout,
    level="INFO",
    filter=lambda record: record["level"].name == "INFO",
    colorize=True,
    format="<blue>[{time:HH:mm:ss}]</blue> <white>{level}</white>: {message}",
)

logger.add(
    sys.stdout,
    level="ERROR",
    filter=lambda record: record["level"].name == "ERROR",
    colorize=True,
    format="<red>[{time:HH:mm:ss}]</red> <level>{level}</level>: <level>{message}</level>",
)

__all__ = ["logger"]
