from typing import Optional, List
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

class FastLangFrameSettings(BaseSettings):
    """Core settings for FastLangFrame projects"""
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    # LLM Settings
    llm_api_key: str = Field(
        default="default_key",
        validation_alias=AliasChoices(
            "llm_api_key",
            "OPENAI_API_KEY",
            "AZURE_OPENAI_API_KEY",
            "DEEPSEEK_API_KEY",
            "GEMINI_API_KEY",
            "CLAUDE_API_KEY",
            "LLM_API_KEY"
        )
    )
    llm_endpoint: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices(
            "llm_endpoint",
            "LLM_ENDPOINT",
            "OPENAI_BASE_URL",
            "DEEPSEEK_API_BASE",
            "LOCAL_LLM_ENDPOINT"
        )
    )
    model_name: str = Field(
        default="gpt-4o",
        validation_alias=AliasChoices(
            "model_name",
            "MODEL_NAME",
            "OPENAI_MODEL_NAME",
            "DEEPSEEK_MODEL_NAME",
            "GEMINI_MODEL_NAME",
            "CLAUDE_MODEL_NAME",
            "LOCAL_LLM_MODEL"
        )
    )
    
    # Azure OpenAI Specific
    azure_openai_api_key: Optional[str] = Field(default=None, alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = Field(default=None, alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = Field(default="2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION")
    azure_deployment_name: Optional[str] = Field(default=None, alias="AZURE_DEPLOYMENT_NAME")

    deep_thinking_model_name: Optional[str] = None
    light_thinking_model_name: Optional[str] = None
    llm_timeout_sec: int = 60

    # DB Settings
    redis_url: Optional[str] = None
    opensearch_url: Optional[str] = None
    database_url: Optional[str] = None

    # MCP Settings
    mcp_server_url: Optional[str] = None
    mcp_server_api_key: Optional[str] = None
    mcp_server_name: Optional[str] = None

    # Tracing (e.g. Phoenix)
    phoenix_enabled: bool = False
    phoenix_endpoint: Optional[str] = None
    project_name: str = "fastlangframe-agent"

_settings_instance: Optional[FastLangFrameSettings] = None

def get_settings() -> FastLangFrameSettings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = FastLangFrameSettings()
    return _settings_instance
