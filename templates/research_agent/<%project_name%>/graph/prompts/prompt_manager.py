import importlib
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Type

from jinja2 import Template
from langchain_core.messages import BaseMessage, SystemMessage
from pydantic import BaseModel

from <%project_name%>.common.config import mari_config
from <%project_name%>.common.mcp import get_ax_mcp_prompt_messages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROMPT_BASE_PATH = "<%project_name%>.graph.prompts"


class PromptTag(str, Enum):
    default = "default"

    @classmethod
    def to_company_prompt_tag(cls, company_code: str = "") -> str:
        # 기본 'default' 태그를 반환하도록 고정
        return cls.default.value

    @classmethod
    def to_prompt_tag(cls, prompt_code: str) -> str:
        tag_name = f"code_{prompt_code}"
        if hasattr(cls, tag_name):
            return getattr(cls, tag_name).value
        return cls.default.value


# Todo: AxPromptCache 잔여 작업 필요
class AxPromptCache:
    def __init__(self, cache_duration_hours: int = 1):
        self._cache: dict[str, dict] = {}
        self._cache_duration = timedelta(hours=cache_duration_hours)

    def _get_cache_key(self, prompt_tags: list[str]) -> str:
        return "_".join(sorted(prompt_tags))

    async def get(self, prompt_tags: list[str]) -> Any | None:
        cache_key = self._get_cache_key(prompt_tags)
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            cached_time = cache_entry["timestamp"]

            if datetime.now() - cached_time <= self._cache_duration:
                logger.debug(f"Cache hit for tags: {prompt_tags}")
                return cache_entry["data"]
            else:
                logger.info(f"Cache expired for tags: {prompt_tags}")
                del self._cache[cache_key]

        logger.info(f"Loading fresh prompt for tags: {prompt_tags}")
        try:
            prompt_messages = await get_ax_mcp_prompt_messages(prompt_tags)
            self.set(prompt_tags, prompt_messages)
            return prompt_messages
        except Exception as e:
            logger.error(f"Failed to load prompt from MCP for tags {prompt_tags}: {e}")

    def set(self, prompt_tags: list[str], data: Any) -> None:
        cache_key = self._get_cache_key(prompt_tags)
        self._cache[cache_key] = {"data": data, "timestamp": datetime.now()}
        logger.info(f"Cached prompt for tags: {prompt_tags}")

    def get_cache_info(self) -> dict[str, int]:
        valid_entries = 0
        expired_entries = 0
        now = datetime.now()

        for entry in self._cache.values():
            if now - entry["timestamp"] <= self._cache_duration:
                valid_entries += 1
            else:
                expired_entries += 1

        return {
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
        }

    def clear_prompt_cache(self) -> None:
        """전체 캐시를 삭제합니다."""
        self._cache.clear()
        logger.info("Cleared all prompt cache entries")


_ax_prompt_cache = AxPromptCache(cache_duration_hours=1)


def set_ax_prompt_cache(prompts: dict):
    for key, resource in prompts.items():
        _ax_prompt_cache.set(key, resource)
    pass


def _get_local_prompt_message(
    company_tag: str, prompt_tags: list[str], prompt_type: str
) -> list[SystemMessage]:
    if not prompt_tags:
        raise ValueError("Tags list is empty")

    submodule = "__".join(prompt_tags)
    module_path = f"{PROMPT_BASE_PATH}.{company_tag}.{submodule}"

    try:
        prompt_module = importlib.import_module(module_path)

    except ImportError as e:
        logger.warning(f"Import error: {e}")
        company_tag = PromptTag.to_company_prompt_tag()  # default company tag
        module_path = f"{PROMPT_BASE_PATH}.{company_tag}.{submodule}"
        prompt_module = importlib.import_module(module_path)

    if hasattr(prompt_module, prompt_type):
        system_prompt = getattr(prompt_module, prompt_type)
        return [SystemMessage(content=system_prompt)]
    else:
        raise ValueError(f"No '{prompt_type}' found in module: {module_path}")


def _get_format_instructions(output_type: Type[BaseModel]) -> str:
    schema = {
        k: v
        for k, v in output_type.model_json_schema().items()
        if k not in ("title", "type")
    }
    format_instructions = json.dumps(
        schema,
        ensure_ascii=False,
        separators=(",", ": "),
        indent=2,
    )
    return format_instructions


async def build_formatted_prompts(
    company_code: str,
    node_name: str,
    prompt_codes: list[str] = [],
    prompt_type: str = "system_prompt",
    output_type: Type[BaseModel] | None = None,
    **kwargs,
) -> list[BaseMessage]:
    """
    MCP에서 node_id로 tagginge된 프롬프트 메시지를 조회하여,
    템플릿 변수와 출력 모델 스키마를 적용한 메시지 객체 리스트로 반환합니다.

    각 메시지는 SystemMessage 또는 HumanMessage 템플릿으로 변환되며,
    output_model이 지정된 경우 해당 모델의 JSON 스키마(response_format)가 템플릿 변수에 포함됩니다.
    """
    try:
        company_tag = PromptTag.to_company_prompt_tag(company_code)
        prompt_tags = [node_name]
        for tag in prompt_codes:
            prompt_tags.append(PromptTag.to_prompt_tag(tag))

        if mari_config.AX_MCP_PROMPT_ENABLED:
            try:
                prompt_messages = await _ax_prompt_cache.get(prompt_tags)
            except Exception as e:
                logger.warning(f"Failed to get cached prompt for {prompt_tags}: {e}")
                prompt_messages = _get_local_prompt_message(
                    company_tag, prompt_tags, prompt_type
                )
        else:
            prompt_messages = _get_local_prompt_message(
                company_tag, prompt_tags, prompt_type
            )

        template_kwargs = {**kwargs}

        if output_type:
            response_format = _get_format_instructions(output_type)
            template_kwargs["response_format"] = response_format

        templated_messages = []
        for message in prompt_messages:
            templated_message = message.model_copy()
            templated_message.content = Template(message.content).render(
                **template_kwargs
            )
            templated_messages.append(templated_message)

        return templated_messages

    except KeyError as e:
        missing_var = str(e).strip("'\"")
        available_vars = list(kwargs.keys())
        raise ValueError(
            f"Missing required template variable '{missing_var}'\nAvailable variables: {available_vars}"
        ) from e
    except Exception as e:
        raise ValueError(f"Failed to format prompt: {str(e)}") from e
