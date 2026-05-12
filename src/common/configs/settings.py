import os
import json
from typing import Optional, List, Dict, Any, Literal
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class FastLangFrameSettings(BaseSettings):
    """Core settings for FastLangFrame projects"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        protected_namespaces=("settings_",),
    )

    # LLM Provider Choice
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")

    # OpenAI Settings
    openai_api_key: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("OPENAI_API_KEY", "LLM_API_KEY")
    )
    openai_model_name: str = Field(
        default="gpt-4o",
        validation_alias=AliasChoices("OPENAI_MODEL_NAME", "MODEL_NAME"),
    )
    openai_api_base: Optional[str] = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices(
            "OPENAI_API_BASE", "LLM_API_BASE", "LLM_ENDPOINT"
        ),
    )

    # Azure OpenAI Settings
    azure_openai_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("AZURE_OPENAI_API_KEY", "LLM_API_KEY"),
    )
    azure_openai_endpoint: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "AZURE_OPENAI_ENDPOINT", "LLM_API_BASE", "LLM_ENDPOINT"
        ),
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION"
    )
    azure_openai_deployment_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("AZURE_OPENAI_DEPLOYMENT_NAME", "MODEL_NAME"),
    )

    # Google Gemini Settings
    google_api_key: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("GOOGLE_API_KEY", "LLM_API_KEY")
    )
    gemini_model_name: str = Field(
        default="gemini-1.5-pro",
        validation_alias=AliasChoices("GEMINI_MODEL_NAME", "MODEL_NAME"),
    )

    # Anthropic Claude Settings
    anthropic_api_key: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("ANTHROPIC_API_KEY", "LLM_API_KEY")
    )
    claude_model_name: str = Field(
        default="claude-3-5-sonnet-20240620",
        validation_alias=AliasChoices("CLAUDE_MODEL_NAME", "MODEL_NAME"),
    )
    anthropic_api_url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "ANTHROPIC_API_URL", "LLM_API_BASE", "LLM_ENDPOINT"
        ),
    )

    # DeepSeek Settings
    deepseek_api_key: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("DEEPSEEK_API_KEY", "LLM_API_KEY")
    )
    deepseek_model_name: str = Field(
        default="deepseek-chat",
        validation_alias=AliasChoices("DEEPSEEK_MODEL_NAME", "MODEL_NAME"),
    )
    deepseek_api_base: str = Field(
        default="https://api.deepseek.com",
        validation_alias=AliasChoices(
            "DEEPSEEK_API_BASE", "LLM_API_BASE", "LLM_ENDPOINT"
        ),
    )

    # Local LLM Settings
    local_llm_endpoint: str = Field(
        default="http://localhost:11434/v1",
        validation_alias=AliasChoices(
            "LOCAL_LLM_ENDPOINT", "LLM_API_BASE", "LLM_ENDPOINT"
        ),
    )
    local_llm_model: str = Field(
        default="llama3", validation_alias=AliasChoices("LOCAL_LLM_MODEL", "MODEL_NAME")
    )

    llm_timeout_sec: int = 60

    # Redis Settings
    # Redis Settings
    redis_url: Optional[str] = None

    # Opensearch Settings
    opensearch_url: Optional[str] = None

    # MCP Settings
    mcp_server_url: Optional[str] = None
    mcp_server_api_key: Optional[str] = None
    mcp_server_name: Optional[str] = None

    # Tracing
    project_name: str = "fastlangframe-agent"

    # Multi-Model Configuration (JSON string)
    llm_models_json: Optional[str] = Field(default=None, alias="LLM_MODELS_JSON")

    # Native JWT Configuration
    jwt_secret_key: str = Field(
        default="your_jwt_secret_key_at_least_32_chars_long", alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=60, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Authelia Configuration
    authelia_url: Optional[str] = Field(default=None, alias="AUTHELIA_URL")
    authelia_introspection_url: Optional[str] = Field(
        default=None, alias="AUTHELIA_INTROSPECTION_URL"
    )
    authelia_token_url: Optional[str] = Field(default=None, alias="AUTHELIA_TOKEN_URL")
    authelia_userinfo_url: Optional[str] = Field(
        default=None, alias="AUTHELIA_USERINFO_URL"
    )
    authelia_authorization_url: Optional[str] = Field(
        default=None, alias="AUTHELIA_AUTHORIZATION_URL"
    )
    authelia_client_id: Optional[str] = Field(default=None, alias="AUTHELIA_CLIENT_ID")
    authelia_client_secret: Optional[str] = Field(
        default=None, alias="AUTHELIA_CLIENT_SECRET"
    )
    authelia_redirect_uri: Optional[str] = Field(
        default=None, alias="AUTHELIA_REDIRECT_URI"
    )
    authelia_public_key_path: str = Field(
        default="authelia/config/oidc_pub.pem", alias="AUTHELIA_PUBLIC_KEY_PATH"
    )

    # Database Settings
    database_driver: str = Field(
        default="postgresql",
        validation_alias=AliasChoices("database_driver", "DATABASE_DRIVER"),
    )
    database_host: str = Field(
        default="localhost",
        validation_alias=AliasChoices("database_host", "DATABASE_HOST"),
    )
    database_port: int = Field(
        default=5432,
        validation_alias=AliasChoices("database_port", "DATABASE_PORT"),
    )
    database_username: str = Field(
        default="admin",
        validation_alias=AliasChoices("database_username", "DATABASE_USERNAME"),
    )
    database_password: str = Field(
        default="admin",
        validation_alias=AliasChoices("database_password", "DATABASE_PASSWORD"),
    )
    database_dbname: str = Field(
        default="backend",
        validation_alias=AliasChoices("database_dbname", "DATABASE_DBNAME"),
    )
    database_schema: str = Field(
        default="public",
        validation_alias=AliasChoices("database_schema", "DATABASE_SCHEMA"),
    )

    @property
    def database_url(self) -> Optional[str]:
        """Constructs the database URL from components"""
        if not self.database_driver:
            return None
        return f"{self.database_driver}://{self.database_username}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_dbname}"

    @property
    def llm_models(self) -> Dict[str, Dict[str, Any]]:
        """Parses the JSON model configuration into a dictionary"""
        if not self.llm_models_json:
            return {}
        try:
            return json.loads(self.llm_models_json)
        except json.JSONDecodeError:
            return {}


_settings_instance: Optional[FastLangFrameSettings] = None


def get_settings() -> FastLangFrameSettings:
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = FastLangFrameSettings()
    return _settings_instance
