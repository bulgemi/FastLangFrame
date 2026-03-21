import logging
from typing import Callable, Any
from src.common.exceptions.custom import FastLangFrameBaseError

logger = logging.getLogger(__name__)

async def handle_agent_exceptions(func: Callable, *args, **kwargs) -> Any:
    """A generic wrapper to catch exceptions and log them at the framework level"""
    try:
        if __import__("inspect").iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    except FastLangFrameBaseError as e:
        logger.error(f"FastLangFrame internal error caught in middleware: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error caught in middleware: {str(e)}", exc_info=True)
        raise
