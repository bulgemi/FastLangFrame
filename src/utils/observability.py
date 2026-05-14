import logging
from typing import Optional, List, Dict, Any
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from src.common.configs.settings import get_settings

logger = logging.getLogger(__name__)

# Global Langfuse client instance to be reused
_langfuse_client: Optional[Langfuse] = None


def get_langfuse_client() -> Optional[Langfuse]:
    """
    Returns a singleton Langfuse client instance.
    """
    global _langfuse_client
    if _langfuse_client is None:
        settings = get_settings()
        if settings.langfuse_public_key and settings.langfuse_secret_key:
            try:
                _langfuse_client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host,
                )
            except Exception as e:
                logger.error(f"Failed to initialize Langfuse client: {e}")
    return _langfuse_client


def get_langfuse_callback(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> Optional[CallbackHandler]:
    """
    Returns a Langfuse CallbackHandler for LangChain/LangGraph tracing.
    
    Note: In Langfuse v3+, user_id, session_id, and tags are best passed 
    via metadata in the LangChain invoke/stream call for root-level traces.
    This function returns a handler that will pick up those attributes 
    if they are present in the 'metadata' dict of the request.
    """
    client = get_langfuse_client()
    if not client:
        return None

    settings = get_settings()

    # In v3+, CallbackHandler init only accepts public_key, update_trace, and trace_context.
    # We use the public_key from settings to ensure we get the correct client instance.
    return CallbackHandler(
        public_key=settings.langfuse_public_key,
        update_trace=True
    )


def prepare_langfuse_metadata(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    tags: Optional[List[str]] = None,
    existing_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prepares metadata dictionary with Langfuse-specific keys that CallbackHandler
    will automatically recognize to set trace attributes.
    """
    metadata = existing_metadata.copy() if existing_metadata else {}
    
    if user_id:
        metadata["langfuse_user_id"] = user_id
    if session_id:
        metadata["langfuse_session_id"] = session_id
    if tags:
        metadata["langfuse_tags"] = tags
        
    return metadata
