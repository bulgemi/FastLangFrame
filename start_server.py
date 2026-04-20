import uvicorn
from unittest.mock import AsyncMock
from src.core.server import create_agent_app

# Create a mock graph for testing
mock_graph = AsyncMock()
mock_graph.ainvoke.return_value = {"messages": [{"role": "assistant", "content": "Hello from mock backend!"}]}

# Create the app
app = create_agent_app(mock_graph)

if __name__ == "__main__":
    print("Starting temporary test server on port 8888...")
    uvicorn.run(app, host="127.0.0.1", port=8888)
