class FastLangFrameBaseError(Exception):
    """Base exception for all FastLangFrame errors"""
    pass

class AgentRuntimeError(FastLangFrameBaseError):
    """Raised when the agent runtime encounters a fatal issue"""
    pass

class ConnectorError(FastLangFrameBaseError):
    """Raised when an external connector (LLM, DB, HTTP) fails"""
    pass

class LLMGenerationError(FastLangFrameBaseError):
    """Raised when LLM fails to generate a valid response"""
    pass

class RuntimeRegistryNotReadyError(FastLangFrameBaseError):
    """Raised when trying to access runtime resources before initialization"""
    pass
