import httpx
from typing import Optional, Any
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
        base_url=settings.openai_api_base,
        api_key=settings.openai_api_key,
        http_client=httpx.AsyncClient(verify=False, timeout=settings.llm_timeout_sec)
    )

@log_connector
def get_langchain_chat_model(model_name: Optional[str] = None, settings: Optional[Any] = None) -> BaseChatModel:
    """Returns a Langchain Chat Model based on the provider settings"""
    if not settings:
        settings = get_settings()
    
    provider = settings.llm_provider.lower()
    
    # Azure OpenAI logic
    if provider == "azure":
        api_key = settings.azure_openai_api_key
        if not api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not set in your .env file.")
        return AzureChatOpenAI(
            deployment_name=model_name or settings.azure_openai_deployment_name or settings.openai_model_name,
            openai_api_key=SecretStr(api_key),
            azure_endpoint=settings.azure_openai_endpoint,
            openai_api_version=settings.azure_openai_api_version,
            validate_base_url=False,
        )
    
    # Claude (Anthropic) logic
    if provider in ["claude", "anthropic"]:
        api_key = settings.anthropic_api_key
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set in your .env file.")
        return ChatAnthropic(
            model_name=model_name or settings.claude_model_name,
            anthropic_api_key=SecretStr(api_key),
            anthropic_api_url=settings.anthropic_api_url,
        )
        
    # Gemini (Google) logic
    if provider in ["gemini", "google"]:
        api_key = settings.google_api_key
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set in your .env file.")
        return ChatGoogleGenerativeAI(
            model=model_name or settings.gemini_model_name,
            google_api_key=SecretStr(api_key),
        )

    # DeepSeek logic
    if provider == "deepseek":
        api_key = settings.deepseek_api_key
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY is not set in your .env file.")
        return ChatOpenAI(
            model_name=model_name or settings.deepseek_model_name,
            openai_api_key=SecretStr(api_key),
            openai_api_base=settings.deepseek_api_base,
            http_client=httpx.Client(verify=False, timeout=settings.llm_timeout_sec)
        )

    # Local LLM logic
    if provider == "local":
        return ChatOpenAI(
            model_name=model_name or settings.local_llm_model,
            openai_api_key=SecretStr("dummy"),
            openai_api_base=settings.local_llm_endpoint,
            http_client=httpx.Client(verify=False, timeout=settings.llm_timeout_sec)
        )
    
    # Default: Standard OpenAI logic
    api_key = settings.openai_api_key
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in your .env file.")
    return ChatOpenAI(
        model_name=model_name or settings.openai_model_name,
        openai_api_key=SecretStr(api_key),
        openai_api_base=settings.openai_api_base,
        http_client=httpx.Client(verify=False, timeout=settings.llm_timeout_sec)
    )

@log_connector
def get_llm_by_role(role: str, settings: Optional[Any] = None) -> BaseChatModel:
    """
    Returns a Langchain Chat Model based on a logical role defined in settings.llm_models.
    Example JSON in .env:
    LLM_MODELS_JSON='{"fast": {"provider": "openai", "model": "gpt-4o-mini"}, "smart": {"provider": "azure", "deployment": "gpt-4o"}}'
    """
    if not settings:
        settings = get_settings()
    models = settings.llm_models
    
    if role not in models:
        # Fallback to default if role not found
        return get_langchain_chat_model(settings=settings)
    
    config = models[role]
    provider = config.get("provider", settings.llm_provider).lower()
    
    if provider == "azure":
        return AzureChatOpenAI(
            deployment_name=config.get("deployment") or config.get("model") or settings.azure_openai_deployment_name,
            openai_api_key=SecretStr(config.get("api_key") or settings.azure_openai_api_key),
            azure_endpoint=config.get("endpoint") or settings.azure_openai_endpoint,
            openai_api_version=config.get("api_version") or settings.azure_openai_api_version,
            validate_base_url=False,
        )
    
    if provider in ["claude", "anthropic"]:
        return ChatAnthropic(
            model_name=config.get("model") or config.get("deployment") or settings.claude_model_name,
            anthropic_api_key=SecretStr(config.get("api_key") or settings.anthropic_api_key),
            anthropic_api_url=config.get("endpoint") or settings.anthropic_api_url,
        )
        
    if provider in ["gemini", "google"]:
        api_key = config.get("api_key") or settings.google_api_key
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set or invalid for role {role}.")
        return ChatGoogleGenerativeAI(
            model=config.get("model") or config.get("deployment") or settings.gemini_model_name,
            google_api_key=SecretStr(api_key),
        )
    
    # Default to OpenAI logic for other providers
    return ChatOpenAI(
        model_name=config.get("model") or config.get("deployment") or settings.openai_model_name,
        openai_api_key=SecretStr(config.get("api_key") or settings.openai_api_key),
        openai_api_base=config.get("endpoint") or settings.openai_api_base,
        http_client=httpx.Client(verify=False, timeout=settings.llm_timeout_sec)
    )
