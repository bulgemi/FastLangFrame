from typing import Optional, List
from langfuse.langchain import CallbackHandler
from src.common.configs.settings import get_settings

def get_langfuse_callback(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Optional[CallbackHandler]:
    """
    Initializes and returns a Langfuse CallbackHandler if configuration is present.
    
    Args:
        user_id: The ID of the user for tracing.
        session_id: The session ID for grouping traces.
        tags: List of tags to attach to the trace.
        
    Returns:
        A Langfuse CallbackHandler instance if configured, otherwise None.
    """
    settings = get_settings()
    
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return None
        
    return CallbackHandler(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
        user_id=user_id,
        session_id=session_id,
        tags=tags or []
    )
