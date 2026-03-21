from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class FastLangFrameSettings(BaseSettings):
    """Core settings for FastLangFrame projects"""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM Settings
    llm_api_key: str = "default_key"
    llm_endpoint: str = "https://api.openai.com/v1"
    model_name: str = "gpt-4o"
    
    # Azure OpenAI Specific
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_version: str = "2024-02-15-preview"
    azure_deployment_name: Optional[str] = None

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
