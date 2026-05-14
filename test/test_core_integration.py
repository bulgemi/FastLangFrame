import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from src.core.server import create_agent_app, authenticated_user
from src.core.api_models import AgentInvokeRequest

@pytest.fixture
def mock_graph():
    graph = AsyncMock()
    graph.ainvoke.return_value = {"output": "hello"}
    return graph

@pytest.fixture
def client(mock_graph):
    app = create_agent_app(mock_graph)
    # Override authentication
    mock_user = {"sub": "user-123", "name": "Test User"}
    app.dependency_overrides[authenticated_user] = lambda: mock_user
    return TestClient(app)

def test_invoke_injects_langfuse_callback(client, mock_graph):
    with patch("src.core.server.get_langfuse_callback") as mock_get_callback:
        mock_callback = MagicMock()
        mock_get_callback.return_value = mock_callback
        
        payload = {
            "input": {"messages": "hi"},
            "config": {"configurable": {"thread_id": "thread-456"}}
        }
        
        response = client.post("/invoke", json=payload)
        
        assert response.status_code == 200
        
        # Verify get_langfuse_callback was called with correct metadata
        mock_get_callback.assert_called_once()
        args, kwargs = mock_get_callback.call_args
        assert kwargs["user_id"] == "user-123"
        assert kwargs["session_id"] == "thread-456"
        
        # Verify graph.ainvoke was called with the callback in config
        mock_graph.ainvoke.assert_called_once()
        call_args, call_kwargs = mock_graph.ainvoke.call_args
        # graph.ainvoke(input, config)
        config = call_args[1] if len(call_args) > 1 else call_kwargs.get("config")
        assert mock_callback in config["callbacks"]
