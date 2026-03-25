import httpx
from typing import Optional
from openai import AsyncOpenAI
from langchain_openai import ChatOpenAI, AzureChatOpenAI
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
