import json
import logging
from typing import Dict, Optional

from pydantic import Field, AliasChoices, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Tavily 기본 설정
DEFAULT_TAVILY_CONFIG = {
    "search_params": {
        "topic": "general",
        "search_depth": "advanced",
        "max_results": 15,  # tavaily에서 최대 20개까지 지원
        "include_domains": [],
        "exclude_domains": ["yahoo.com"],
    },
    "result_filter": {"score_threshold": 0.6, "extract_publish_date_by_url": False},
}


class MariAgentConfig(BaseSettings):
    """Market Intelligence Agent Configuration"""

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"], env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # LLM 관련 설정
    llm_provider: str = Field(
        default="openai",
        alias="LLM_PROVIDER",
        description="LLM Provider (openai, gemini, azure, etc.)",
    )
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    gemini_model_name: str = Field(default="gemini-1.5-pro", alias="GEMINI_MODEL_NAME")
    llm_api_key: str = Field(
        default="sk-2e9622c660cf089567e7967a5a7d481b",
        validation_alias=AliasChoices("LLM_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"),
        description="LLM API Key",
    )
    llm_endpoint: str = Field(
        default="https://aip.sktai.io/api/v1/gateway",
        validation_alias=AliasChoices("LLM_ENDPOINT", "OPENAI_BASE_URL", "GOOGLE_BASE_URL"),
        description="LLM API Endpoint",
    )
    llm_model_gpt_4o: str = Field(
        default="openai_skmidev-azure-openai-gpt-4o-20241120",
        validation_alias=AliasChoices("LLM_MODEL_GPT_4o", "MODEL_NAME", "OPENAI_MODEL_NAME"),
        description="GPT-4o Model Name",
    )
    llm_model_gpt_4_1: str = Field(
        default="skmidev-gpt-4-1-20250414",
        validation_alias=AliasChoices("LLM_MODEL_GPT_4_1", "MODEL_NAME", "OPENAI_MODEL_NAME"),
        description="GPT-4.1 Model Name",
    )

    # Data Collect 설정
    data_collect_max_concurrent_tasks: Optional[int] = Field(
        default=5,
        alias="DATA_COLLECT_MAX_CONCURRENT_TASKS",
        description="Data Collect Max Concurrent Tasks",
    )

    data_collect_task_timeout: Optional[int] = Field(
        default=30,
        alias="DATA_COLLECT_TASK_TIMEOUT",
        description="Data Collect Task Timeout in seconds",
    )

    # web search Tavily 설정
    tavily_config_json: Optional[str] = Field(
        default=json.dumps(DEFAULT_TAVILY_CONFIG),
        alias="TAVILY_CONFIG_JSON",
        description="Tavily 설정 JSON 문자열. Tavily 사용 시에만 필요",
    )
    tavily_api_key: Optional[str] = Field(
        default="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",
        alias="TAVILY_API_KEY",
        description="Tavily API Key(ax_mcp_tavily_enabled==True이면, 필수)",
    )
    tavily_score_threshold: Optional[float] = Field(
        default=0.7,
        alias="TAVILY_SCORE_THRESHOLD",
        description="Tavily Score Threshold(ax_mcp_tavily_enabled==True이면, 필수)",
    )
    tavily_max_concurrent_requests: Optional[int] = Field(
        default=15,
        alias="TAVILY_MAX_CONCURRENT_REQUESTS",
        description="Tavily Max Concurrent Requests",
    )

    # AX MCP SERVER 기본 설정
    ax_mcp_server_url: str = Field(
        default="http://127.0.0.1:8080/mcp",
        alias="AX_MCP_SERVER_URL",
        description="AX MCP Server URL",
    )
    ax_mcp_server_api_key: str = Field(
        default="dummy",
        alias="AX_MCP_SERVER_API_KEY",
        description="AX MCP Server API Key",
    )
    ax_mcp_server_name: str = Field(
        default="aix-mcp-remote",
        alias="AX_MCP_SERVER_NAME",
        description="AX MCP Server Name",
    )

    # AX MCP SERVER - Inference Prompt 설정
    ax_mcp_prompt_enabled: bool = Field(
        default=False,
        alias="AX_MCP_PROMPT_ENABLED",
        description="Enable MARI Tag Group for MCP Prompts",
    )
    ax_mcp_prompt_mari_tag_group: str = Field(
        default="research_agent",
        alias="AX_MCP_PROMPT_MARI_TAG_GROUP",
        description="MARI Tag Group for MCP Prompts",
    )
    ax_mcp_prompt_list_url: str = Field(
        default="prompt://ax_platform/tags/",
        alias="AX_MCP_PROMPT_LIST_URL",
        description="MCP Prompt List URL",
    )
    ax_mcp_prompt_message_by_tag: str = Field(
        default="prompt://ax_platform/messages/tags/{tags}/latest",
        alias="AX_MCP_PROMPT_MESSAGE_BY_TAG",
        description="MCP Prompt Message by Tag URL Template",
    )
    ax_mcp_prompt_message_by_id: str = Field(
        default="prompt://ax_platform/messages/{prompt_id}",
        alias="AX_MCP_PROMPT_MESSAGE_BY_ID",
        description="MCP Prompt Message by ID URL Template",
    )

    # AX PLATFORM Remote Agent 설정
    aip_model_endpoint: Optional[str] = Field(
        default=None, alias="AIP_MODEL_ENDPOINT", description="AIP Model Endpoint"
    )
    ax_platform_agent_aip_name: Optional[str] = Field(
        default=None,
        alias="AX_PLATFORM_AGENT_AIP_NAME",
        description="AX Platform Agent AIP Name",
    )

    latest_histories_cnt: int = Field(
        default=10,
        alias="LATEST_HISTORIES_CNT",
        description="최신 대화 내역 반영 개수",
    )

    @model_validator(mode="after")
    def validate_critical_configs(self):
        """중요한 설정 검증"""
        critical_fields = [
            "llm_api_key",
            "llm_endpoint",
            "llm_model_gpt_4_1",
            "ax_mcp_server_url",
            "ax_mcp_server_api_key",
            "ax_mcp_server_name",
        ]

        missing_configs = []
        for field in critical_fields:
            value = getattr(self, field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_configs.append(field.upper())

        if missing_configs:
            logger.warning(f"Missing critical configs: {', '.join(missing_configs)}")

        return self

    # 호환성을 위한 프로퍼티들 (기존 코드와의 호환성 유지)
    @property
    def LLM_API_KEY(self) -> str:
        return self.llm_api_key

    @property
    def LLM_ENDPOINT(self) -> str:
        return self.llm_endpoint

    @property
    def LLM_MODEL_GPT_4o(self) -> str:
        return self.llm_model_gpt_4o

    @property
    def LLM_MODEL_GPT_4_1(self) -> str:
        return self.llm_model_gpt_4_1

    @property
    def AX_MCP_SERVER_URL(self) -> str:
        return self.ax_mcp_server_url

    @property
    def AX_MCP_SERVER_API_KEY(self) -> str:
        return self.ax_mcp_server_api_key

    @property
    def AX_MCP_SERVER_NAME(self) -> str:
        return self.ax_mcp_server_name

    @property
    def AX_MCP_PROMPT_ENABLED(self) -> bool:
        return self.ax_mcp_prompt_enabled

    @property
    def AX_MCP_PROMPT_MARI_TAG_GROUP(self) -> str:
        return self.ax_mcp_prompt_mari_tag_group

    @property
    def AX_MCP_PROMPT_LIST_URL(self) -> str:
        return self.ax_mcp_prompt_list_url

    @property
    def AX_MCP_PROMPT_MESSAGE_BY_TAG(self) -> str:
        return self.ax_mcp_prompt_message_by_tag

    @property
    def AX_MCP_PROMPT_MESSAGE_BY_ID(self) -> str:
        return self.ax_mcp_prompt_message_by_id

    @property
    def AIP_MODEL_ENDPOINT(self) -> Optional[str]:
        return self.aip_model_endpoint

    @property
    def AX_PLATFORM_AGENT_AIP_NAME(self) -> Optional[str]:
        return self.ax_platform_agent_aip_name

    @property
    def LATEST_HISTORIES_CNT(self) -> int:
        return self.latest_histories_cnt

    @property
    def DATA_COLLECT_MAX_CONCURRENT_TASKS(self) -> Optional[int]:
        return self.data_collect_max_concurrent_tasks

    @property
    def DATA_COLLECT_TASK_TIMEOUT(self) -> Optional[int]:
        return self.data_collect_task_timeout

    @property
    def TAVILY_CONFIG_JSON(self) -> Dict:
        try:
            config = json.loads(self.tavily_config_json)
            merged_config = DEFAULT_TAVILY_CONFIG.copy()
            merged_config.update(config)
            return merged_config
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse env config: {e}. Using default config.")
            return DEFAULT_TAVILY_CONFIG.copy()

    @property
    def TAVILY_API_KEY(self) -> Optional[str]:
        return self.tavily_api_key

    @property
    def TAVILY_SCORE_THRESHOLD(self) -> Optional[float]:
        return self.tavily_score_threshold

    @property
    def TAVILY_MAX_CONCURRENT_REQUESTS(self) -> Optional[int]:
        return self.tavily_max_concurrent_requests


class PhoenixConfig(BaseSettings):
    """Tracing with Phoenix"""

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"], env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    enabled: bool = Field(
        default=False,
        alias="PHOENIX_TRACER__ENABLED",
        description="Enable Phoenix tracing",
    )
    endpoint: str = Field(
        default="http://aip.sktai.io/phoenix/v1/traces",
        alias="PHOENIX_TRACER__ENDPOINT",
        description="Phoenix tracing endpoint",
        examples=[
            "http://phoenix:4317",
            "http://phoenix:6006/v1/traces",
            "http://aip.sktai.io/phoenix/v1/traces",
        ],
    )
    graphql_endpoint: str = Field(
        default="https://aip.sktai.io/phoenix/graphql",
        alias="PHOENIX_TRACER__GRAPHQL_ENDPOINT",
        description="Phoenix GraphQL endpoint",
    )
    verbose: bool = Field(
        default=False,
        alias="PHOENIX_TRACER__VERBOSE",
        description="Enable verbose logging for Phoenix",
    )
    project_name: str = Field(
        default="default",
        alias="PHOENIX_TRACER__PROJECT_NAME",
        description="배포된 app에서 tracing 할 때 사용하는 project_name. Serving Request시 agent_param에 담고, app 뜰 때 env로 주입",
    )
    phoenix_apikey: Optional[str] = Field(
        default=None,
        alias="PHOENIX_TRACER__API_KEY",
        description="Phoenix API Key. Phoenix가 Auth 적용 안되어있으면 필요 없음",
    )

    @field_validator("verbose", "enabled", mode="before")
    def _bool(cls, v):
        if isinstance(v, bool):
            return v

        elif isinstance(v, str):
            if v.lower() == "false":
                return False
            elif v.lower() == "true":
                return True
            else:
                return False

        else:
            return False


# 싱글톤 인스턴스들
_phoenix_config: Optional[PhoenixConfig] = None
_mari_config: Optional[MariAgentConfig] = None


def get_phoenix_config() -> PhoenixConfig:
    """Phoenix 설정 인스턴스 반환 (싱글톤)"""
    global _phoenix_config
    if _phoenix_config is None:
        _phoenix_config = PhoenixConfig()
    return _phoenix_config


def get_mari_config() -> MariAgentConfig:
    """MARI Agent 설정 인스턴스 반환 (싱글톤)"""
    global _mari_config
    if _mari_config is None:
        _mari_config = MariAgentConfig()
    return _mari_config


# 호환성을 위한 전역 변수들
phoenix_config = get_phoenix_config()
mari_config = get_mari_config()


def get_mcp_connections() -> Dict:
    """MCP 연결 설정 반환"""
    config = get_mari_config()
    return {
        config.AX_MCP_SERVER_NAME: {
            "transport": "streamable_http",
            "url": config.AX_MCP_SERVER_URL,
            "headers": {"Authorization": f"Bearer {config.AX_MCP_SERVER_API_KEY}"},
            "session_kwargs": {
                "client_info": {
                    "name": "agent-backend-builder",
                    "version": "0.1",
                },
            },
        }
    }


# 호환성을 위한 전역 변수
MCP_CONNECTIONS = get_mcp_connections()
