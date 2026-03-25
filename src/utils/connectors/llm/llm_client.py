import httpx
from typing import Optional
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from src.common.configs.settings import FastLangFrameSettings, get_settings
from src.common.logging.decorators import log_connector

@log_connector
async def get_async_openai_client(settings: Optional[FastLangFrameSettings] = None) -> AsyncOpenAI:
    """Returns the raw OpenAI Async client"""
    if not settings:
        settings = get_settings()
    return AsyncOpenAI(
        base_url=settings.llm_endpoint,
        api_key=settings.llm_api_key,
        http_client=httpx.AsyncClient(verify=False, timeout=settings.llm_timeout_sec)
    )

@log_connector
def get_langchain_chat_model(model_name: Optional[str] = None) -> ChatOpenAI:
    """Returns a Langchain Chat Model (OpenAI or Azure)"""
    settings = get_settings()
    
    # Azure OpenAI logic (triggered by prefix OR provider choice)
    is_azure = (
        (settings.azure_openai_api_key and settings.azure_openai_endpoint) or 
        (settings.llm_provider.lower() == "azure")
    )
    
    if is_azure:
        deployment = (
            settings.azure_deployment_name or 
            model_name or 
            settings.model_name
        )
        return AzureChatOpenAI(
            azure_deployment=deployment,
            api_key=settings.azure_openai_api_key or settings.llm_api_key,
            azure_endpoint=settings.azure_openai_endpoint or settings.llm_endpoint,
            api_version=settings.azure_openai_api_version,
            validate_base_url=False,
        )
    
    # Standard OpenAI logic
    name_to_use = model_name or settings.model_name
    return ChatOpenAI(
        model=name_to_use,
        api_key=settings.llm_api_key,
        base_url=settings.llm_endpoint,
        http_client=httpx.Client(verify=False, timeout=settings.llm_timeout_sec)
    )

@log_connector
def get_llm_by_role(role: str) -> BaseChatModel:
    """
    Returns a Langchain Chat Model based on a logical role defined in settings.llm_models.
    Example JSON in .env:
    LLM_MODELS_JSON='{"fast": {"provider": "openai", "model": "gpt-4o-mini"}, "smart": {"provider": "azure", "deployment": "gpt-4o"}}'
    """
    settings = get_settings()
    models = settings.llm_models
    
    if role not in models:
        # Fallback to default if role not found
        return get_langchain_chat_model()
    
    config = models[role]
    provider = config.get("provider", "openai").lower()
    
    if provider == "azure":
        return AzureChatOpenAI(
            azure_deployment=config.get("deployment") or config.get("model"),
            api_key=config.get("api_key") or settings.azure_openai_api_key or settings.llm_api_key,
            azure_endpoint=config.get("endpoint") or settings.azure_openai_endpoint or settings.llm_endpoint,
            api_version=config.get("api_version") or settings.azure_openai_api_version,
            validate_base_url=False,
        )
    
    # Default to OpenAI logic for other providers (can be extended)
    return ChatOpenAI(
        model=config.get("model") or config.get("deployment") or settings.model_name,
        api_key=config.get("api_key") or settings.llm_api_key,
        base_url=config.get("endpoint") or settings.llm_endpoint,
        http_client=httpx.Client(verify=False, timeout=settings.llm_timeout_sec)
    )
