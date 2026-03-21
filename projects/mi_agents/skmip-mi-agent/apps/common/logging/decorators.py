from collections.abc import Callable
from functools import wraps
import json
import logging
import sys
import time
from typing import Any, TypeVar

from pydantic import BaseModel

from apps.agents.mi_agent.state.state import MariAgentState
from apps.common.logging.logger_config import logger


T = TypeVar("T", bound=BaseModel)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


def time_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logging.info(f"[{func.__name__}] 실행 시간: {duration:.4f}초")
        return result

    return wrapper


def async_time_logger(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        logging.info(f"[{func.__name__}] 실행 시간: {duration:.4f}초")
        return result

    return wrapper


def log_node(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @wraps(func)
    def wrapper(
        state: MariAgentState,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> T:
        node_name = func.__name__
        logger.info(f"[**NODE**][{node_name}] Input: {state}")
        try:
            result = func(state, *args, **kwargs)
            logger.info(f"[{node_name}] Output: {result}")
        except Exception as e:
            logger.exception(f"[**NODE**][{node_name}] Failed with error: {e}")
            raise
        return result

    return wrapper


def serialize(obj: Any) -> str:
    if isinstance(obj, BaseModel):
        return json.dumps(obj.model_dump(), ensure_ascii=False, indent=2)
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, ensure_ascii=False, indent=2)
    try:
        return str(obj)
    except Exception:
        return repr(obj)


def log_tool(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @wraps(func)
    def wrapper(state: Any, *args: tuple[Any, ...], **kwargs: dict[str, Any]) -> T:
        tool_name = func.__name__

        logger.info(f"[**TOOL**][{tool_name}] Input:\n{serialize(state)}")

        try:
            result = func(state, *args, **kwargs)
            logger.info(f"[**TOOL**][{tool_name}] Output:\n{serialize(result)}")
        except Exception as e:
            logger.exception(f"[**TOOL**][{tool_name}] Failed with error: {e}")
            raise

        return result

    return wrapper


def log_connector(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @wraps(func)
    def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> T:
        connector_name = func.__name__

        logger.info(f"[**CONNECTOR**][{connector_name}] Input:\n{serialize(args)}")

        try:
            result = func(*args, **kwargs)
            logger.info(
                f"[**CONNECTOR**][{connector_name}] Output:\n{serialize(result)}",
            )
        except Exception as e:
            logger.exception(
                f"[**CONNECTOR**][{connector_name}] Failed with error: {e}",
            )
            raise

        return result

    return wrapper


def track_node(
    func: Callable[[MariAgentState], MariAgentState],
) -> Callable[[MariAgentState], MariAgentState]:
    @wraps(func)
    def wrapper(
        state: MariAgentState,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> MariAgentState:
        node_name = func.__name__

        state.current_node = node_name
        state.executed_nodes.append(state.current_node)
        logger.info(
            f"[**TRACK**][node_name:{node_name}][state.executed_nodes:{state.executed_nodes}] ",
        )
        return func(state, *args, **kwargs)

    return wrapper
