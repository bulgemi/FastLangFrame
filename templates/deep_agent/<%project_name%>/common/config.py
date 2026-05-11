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
        "max_results": 15,
        "include_domains": [],
        "exclude_domains": ["yahoo.com"],
    },
    "result_filter": {"score_threshold": 0.6, "extract_publish_date_by_url": False},
}


class FlfAgentConfig(BaseSettings):
    """Market Intelligence Agent Configuration"""

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"], env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # LLM Provider Choice
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")

    # OpenAI Settings
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    openai_model_name: str = Field(default="gpt-4o", alias="OPENAI_MODEL_NAME")
    openai_api_base: str = Field(default="https://api.openai.com/v1", alias="OPENAI_API_BASE")

    # Azure OpenAI Settings
    azure_openai_api_key: Optional[str] = Field(default=None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = Field(default=None, alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = Field(default="2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment_name: Optional[str] = Field(default=None, alias="AZURE_OPENAI_DEPLOYMENT_NAME")

    # Google Gemini Settings
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    gemini_model_name: str = Field(default="gemini-1.5-pro", alias="GEMINI_MODEL_NAME")

    # Anthropic Claude Settings
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    claude_model_name: str = Field(default="claude-3-5-sonnet-20240620", alias="CLAUDE_MODEL_NAME")
    anthropic_api_url: Optional[str] = Field(default=None, alias="ANTHROPIC_API_URL")

    # DeepSeek Settings
    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_model_name: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL_NAME")
    deepseek_api_base: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_API_BASE")

    # Local LLM Settings
    local_llm_endpoint: str = Field(default="http://localhost:11434/v1", alias="LOCAL_LLM_ENDPOINT")
    local_llm_model: str = Field(default="llama3", alias="LOCAL_LLM_MODEL")

    # Compatibility properties for old code (if any)
    @property
    def LLM_API_KEY(self) -> Optional[str]:
        p = self.llm_provider.lower()
        if p == "openai": return self.openai_api_key
        if p == "azure": return self.azure_openai_api_key
        if p == "gemini" or p == "google": return self.google_api_key
        if p == "claude" or p == "anthropic": return self.anthropic_api_key
        if p == "deepseek": return self.deepseek_api_key
        return None

    @property
    def LLM_MODEL_GPT_4o(self) -> str:
        return self.openai_model_name if self.llm_provider == "openai" else self.gemini_model_name

    @property
    def LLM_MODEL_GPT_4_1(self) -> str:
        return self.openai_model_name # Fallback

    # Data Collect 설정
    data_collect_max_concurrent_tasks: Optional[int] = Field(
        default=5,
        alias="DATA_COLLECT_MAX_CONCURRENT_TASKS",
    )

    data_collect_task_timeout: Optional[int] = Field(
        default=30,
        alias="DATA_COLLECT_TASK_TIMEOUT",
    )

    # web search Tavily 설정
    tavily_config_json: Optional[str] = Field(
        default=json.dumps(DEFAULT_TAVILY_CONFIG),
        alias="TAVILY_CONFIG_JSON",
    )
    tavily_api_key: Optional[str] = Field(
        default=None,
        alias="TAVILY_API_KEY",
    )

    # AX MCP SERVER 기본 설정
    ax_mcp_server_url: str = Field(
        default="http://127.0.0.1:8080/mcp",
        alias="AX_MCP_SERVER_URL",
    )
    ax_mcp_server_api_key: str = Field(
        default="dummy",
        alias="AX_MCP_SERVER_API_KEY",
    )
    ax_mcp_server_name: str = Field(
        default="aix-mcp-remote",
        alias="AX_MCP_SERVER_NAME",
    )

    # AX MCP SERVER - Inference Prompt 설정
    ax_mcp_prompt_enabled: bool = Field(
        default=False,
        alias="AX_MCP_PROMPT_ENABLED",
    )
    ax_mcp_prompt_mari_tag_group: str = Field(
        default="<%project_name%>",
        alias="AX_MCP_PROMPT_MARI_TAG_GROUP",
    )

    latest_histories_cnt: int = Field(
        default=10,
        alias="LATEST_HISTORIES_CNT",
    )

    @model_validator(mode="after")
    def validate_critical_configs(self):
        """중요한 설정 검증"""
        # We now validate based on provider
        p = self.llm_provider.lower()
        if p == "openai" and not self.openai_api_key:
            logger.warning("Missing OPENAI_API_KEY")
        elif p == "azure" and not self.azure_openai_api_key:
            logger.warning("Missing AZURE_OPENAI_API_KEY")
        elif (p == "gemini" or p == "google") and not self.google_api_key:
            logger.warning("Missing GOOGLE_API_KEY")
        elif (p == "claude" or p == "anthropic") and not self.anthropic_api_key:
            logger.warning("Missing ANTHROPIC_API_KEY")
        elif p == "deepseek" and not self.deepseek_api_key:
            logger.warning("Missing DEEPSEEK_API_KEY")

        return self


class PhoenixConfig(BaseSettings):
    """Tracing with Phoenix"""

    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"], env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    enabled: bool = Field(
        default=False,
        alias="PHOENIX_TRACER__ENABLED",
    )
    endpoint: str = Field(
        default="http://aip.sktai.io/phoenix/v1/traces",
        alias="PHOENIX_TRACER__ENDPOINT",
    )
    project_name: str = Field(
        default="default",
        alias="PHOENIX_TRACER__PROJECT_NAME",
    )

    @field_validator("enabled", mode="before")
    def _bool(cls, v):
        if isinstance(v, bool): return v
        if isinstance(v, str): return v.lower() == "true"
        return False


_phoenix_config: Optional[PhoenixConfig] = None
_flf_config: Optional[FlfAgentConfig] = None


def get_phoenix_config() -> PhoenixConfig:
    global _phoenix_config
    if _phoenix_config is None:
        _phoenix_config = PhoenixConfig()
    return _phoenix_config


def get_flf_config() -> FlfAgentConfig:
    global _flf_config
    if _flf_config is None:
        _flf_config = FlfAgentConfig()
    return _flf_config


phoenix_config = get_phoenix_config()
flf_config = get_flf_config()
