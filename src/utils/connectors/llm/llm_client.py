import httpx
from typing import Optional
from openai import AsyncOpenAI
from pydantic import SecretStr
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
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
def get_langchain_chat_model(model_name: Optional[str] = None) -> BaseChatModel:
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
            deployment_name=deployment,
            openai_api_key=SecretStr(settings.azure_openai_api_key or settings.llm_api_key),
            azure_endpoint=settings.azure_openai_endpoint or settings.llm_endpoint,
            openai_api_version=settings.azure_openai_api_version,
            validate_base_url=False,
        )
    
    # Claude (Anthropic) logic
    is_claude = (
        settings.anthropic_api_key or 
        (settings.llm_provider.lower() in ["claude", "anthropic"])
    )
    if is_claude:
        return ChatAnthropic(
            model_name=model_name or settings.model_name,
            anthropic_api_key=SecretStr(settings.anthropic_api_key or settings.llm_api_key),
            anthropic_api_url=settings.anthropic_api_url or settings.llm_endpoint if "anthropic" in (settings.llm_endpoint or "") else None,
        )
        
    # Gemini (Google) logic
    is_gemini = (
        settings.google_api_key or 
        (settings.llm_provider.lower() in ["gemini", "google"])
    )
    if is_gemini:
        api_key = settings.google_api_key or settings.llm_api_key
        if not api_key or api_key == "default_key":
            raise ValueError("Gemini API Key is not set or invalid. Please set GOOGLE_API_KEY in your .env file.")
        return ChatGoogleGenerativeAI(
            model=model_name or settings.model_name,
            google_api_key=SecretStr(api_key),
        )
    
    # Standard OpenAI logic
    name_to_use = model_name or settings.model_name
    return ChatOpenAI(
        model_name=name_to_use,
        openai_api_key=SecretStr(settings.llm_api_key),
        openai_api_base=settings.llm_endpoint,
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
            deployment_name=config.get("deployment") or config.get("model"),
            openai_api_key=SecretStr(config.get("api_key") or settings.azure_openai_api_key or settings.llm_api_key),
            azure_endpoint=config.get("endpoint") or settings.azure_openai_endpoint or settings.llm_endpoint,
            openai_api_version=config.get("api_version") or settings.azure_openai_api_version,
            validate_base_url=False,
        )
    
    if provider in ["claude", "anthropic"]:
        return ChatAnthropic(
            model_name=config.get("model") or config.get("deployment") or settings.model_name,
            anthropic_api_key=SecretStr(config.get("api_key") or settings.anthropic_api_key or settings.llm_api_key),
            anthropic_api_url=config.get("endpoint") or settings.anthropic_api_url,
        )
        
    if provider in ["gemini", "google"]:
        api_key = config.get("api_key") or settings.google_api_key or settings.llm_api_key
        if not api_key or api_key == "default_key":
            raise ValueError("Gemini API Key is not set or invalid. Please set GOOGLE_API_KEY in your .env file.")
        return ChatGoogleGenerativeAI(
            model=config.get("model") or config.get("deployment") or settings.model_name,
            google_api_key=SecretStr(api_key),
        )
    
    # Default to OpenAI logic for other providers (can be extended)
    return ChatOpenAI(
        model_name=config.get("model") or config.get("deployment") or settings.model_name,
        openai_api_key=SecretStr(config.get("api_key") or settings.llm_api_key),
        openai_api_base=config.get("endpoint") or settings.llm_endpoint,
        http_client=httpx.Client(verify=False, timeout=settings.llm_timeout_sec)
    )
