from enum import Enum

class ModelPreference(str, Enum):
    QUALITY = "quality"
    SPEED = "speed"

class SemaphoreName(str, Enum):
    HTTP = "http"
    LLM = "llm"
    MCP = "mcp"
