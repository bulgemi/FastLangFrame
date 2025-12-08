from collections.abc import Mapping
from functools import lru_cache
import pathlib
from typing import Any
from uuid import UUID

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = pathlib.Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # A.X Platform
    ai_platform_host_url: str
    api_key: str

    # MODEL
    model_endpoint: str
    model_api_key: str
    model_api_deployment_name: str
    lightly_thinking_model_api_deployment_name: str
    deeply_thinking_model_api_deployment_name: str

    # MCP
    mcp_url: str
    mcp_pool_size: int
    mcp_per_session_limit: int

    # HTTP
    http_timeout: float
    http_connect_timeout: float
    http_verify: bool
    http2: bool
    http_max_connection: int
    http_max_keepalive: int
    http_request_max_retries: int
    http_retry_backoff_base: float

    # VDB
    repo_id: str
    repo_id_rdb_metadata: UUID

    # LLM
    llm_concurrency: int
    llm_timeout_sec: float = Field(default=90.0)

    # WEB
    bing_endpoint: str
    bing_api_key: str

    # CONCURRENCY
    mcp_max_concurrency: int
    http_max_concurrency: int

    # SEARCH
    search_sources: list[str] = Field(default=["rdb", "vdb"])
    search_exec_fanout_deadline_sec: float = Field(default=240.0)
    search_strict_required: bool = Field(default=True)

    search_rdb_exec_timeout_sec: float = 240.0
    search_vdb_exec_timeout_sec: float = 240.0
    search_web_exec_timeout_sec: float = 240.0

    # MCP
    mcp_database_base: str = "mimcp://database"

    @computed_field
    @property
    def mcp_metadata_uri(self) -> str:
        return self.mcp_database_base + "/metas"

    @computed_field
    @property
    def mcp_table_schema_uri(self) -> str:
        return self.mcp_database_base + "/schemas/midb/tables"

    @computed_field
    @property
    def mcp_table_codes_uri(self) -> str:
        return self.mcp_database_base + "/metas/codes"

    # Swagger
    title: str = "Query Knowledge Base Builder"
    version: str = "v0.0.1"

    # time zone
    time_zone: str = "Asia/Seoul"

    openapi_version: str = "/v1"
    openapi_prefix: str = "/api" + openapi_version
    openapi_doc_url: str = openapi_prefix + "/openapi.json"
    openapi_doc_description: str = "skmip-query-pilot App의 REST API는 다음의 OpenAPI Spec을 따른다."
    openapi_docs_url: str = openapi_prefix + "/docs"
    openapi_redoc_url: str = openapi_prefix + "/redoc"

    openapi_metadata_hub_path: str = openapi_prefix + "/metadata_hub"
    openapi_curation_path: str = openapi_metadata_hub_path + "/curation"

    # LOG
    log_level: str
    debug: bool = Field(default=False)

    @property
    def set_backend_app_attributes(self) -> Mapping[str, Any]:
        return {
            "title": self.title,
            "version": self.version,
            "debug": self.debug,
            "description": self.openapi_doc_description,
            "docs_url": self.openapi_docs_url,
            "openapi_url": self.openapi_doc_url,
            "redoc_url": self.openapi_redoc_url,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
