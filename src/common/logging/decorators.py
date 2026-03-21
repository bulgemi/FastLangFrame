import functools
import time
from typing import Callable, Any
from .logger_config import setup_logger

logger = setup_logger("fastlangframe.connectors")

def log_connector(func: Callable) -> Callable:
    """Decorator to log connector calls and errors"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger.info(f"Calling connector: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Connector {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in connector {func.__name__}: {str(e)}")
            raise
            
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger.info(f"Calling connector: {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Connector {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in connector {func.__name__}: {str(e)}")
            raise

    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

def time_logger(func: Callable) -> Callable:
    """Decorator to log execution time"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"Execution of {func.__name__} took {end - start:.4f} seconds")
        return result
        
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"Execution of {func.__name__} took {end - start:.4f} seconds")
        return result

    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
