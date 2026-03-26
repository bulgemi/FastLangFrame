import pytest
from unittest.mock import MagicMock, patch
from pydantic import SecretStr
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from src.utils.connectors.llm.llm_client import (
    get_async_openai_client,
    get_langchain_chat_model,
    get_llm_by_role
)

@pytest.fixture
def mock_settings():
    with patch("src.utils.connectors.llm.llm_client.get_settings") as mock:
        settings = MagicMock()
        settings.llm_endpoint = "https://api.openai.com/v1"
        settings.llm_api_key = "test-key"
        settings.llm_timeout_sec = 30
        settings.model_name = "gpt-4o"
        settings.llm_provider = "openai"
        settings.azure_openai_api_key = None
        settings.azure_openai_endpoint = None
        settings.azure_openai_api_version = "2024-02-15-preview"
        settings.azure_deployment_name = None
        settings.llm_models = {}
        mock.return_value = settings
        yield settings

@pytest.mark.asyncio
async def test_get_async_openai_client(mock_settings):
    client = await get_async_openai_client()
    assert client.base_url == "https://api.openai.com/v1/"
    assert client.api_key == "test-key"

def test_get_langchain_chat_model_openai(mock_settings):
    model = get_langchain_chat_model()
    assert isinstance(model, ChatOpenAI)
    assert model.model_name == "gpt-4o"
    assert model.openai_api_key.get_secret_value() == "test-key"

def test_get_langchain_chat_model_azure(mock_settings):
    mock_settings.llm_provider = "azure"
    mock_settings.azure_deployment_name = "test-deployment"
    mock_settings.azure_openai_api_key = "azure-key"
    mock_settings.azure_openai_endpoint = "https://test.azure.com"
    
    model = get_langchain_chat_model()
    assert isinstance(model, AzureChatOpenAI)
    assert model.deployment_name == "test-deployment"
    assert model.openai_api_key.get_secret_value() == "azure-key"

def test_get_llm_by_role_fallback(mock_settings):
    # Role not in models, should fallback
    model = get_llm_by_role("unknown-role")
    assert isinstance(model, ChatOpenAI)

def test_get_llm_by_role_custom(mock_settings):
    mock_settings.llm_models = {
        "fast": {"provider": "openai", "model": "gpt-4o-mini", "api_key": "fast-key"},
        "smart": {"provider": "azure", "deployment": "gpt-4o-azure", "endpoint": "https://smart.azure.com"}
    }
    
    # Test fast role
    fast_model = get_llm_by_role("fast")
    assert isinstance(fast_model, ChatOpenAI)
    assert fast_model.model_name == "gpt-4o-mini"
    assert fast_model.openai_api_key.get_secret_value() == "fast-key"
    
    # Test smart role
    smart_model = get_llm_by_role("smart")
    assert isinstance(smart_model, AzureChatOpenAI)
    assert smart_model.deployment_name == "gpt-4o-azure"
    assert smart_model.azure_endpoint == "https://smart.azure.com"
