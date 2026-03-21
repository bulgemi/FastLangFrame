from enum import StrEnum


class ModelPreference(StrEnum):
    QUALITY = "quality"
    SPEED = "speed"


class MCPServerCallMode(StrEnum):
    RDB_READ = ("rdb_read",)
    RDB_EXECUTE = ("rdb_execute",)


class SemaphoreName(StrEnum):
    HTTP = "HTTP"
    MCP = "MCP"
    LLM = "LLM"


class SearchSource(StrEnum):
    RDB = "rdb"
    VDB = "vdb"
    WEB = "web"
