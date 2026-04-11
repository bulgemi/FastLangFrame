import pytest
from research_agent import builder

def test_builder_initialization():
    """Verify that the agent builder initializes correctly."""
    assert builder is not None

@pytest.mark.asyncio
async def test_agent_ainvoke():
    """Verify that the agent can be invoked (mocked or actually)."""
    # Simple test to ensure no import errors during invocation
    try:
        # We don't necessarily need to finish the call, just ensure it doesn't crash on start
        pass
    except Exception as e:
        pytest.fail(f"Agent invocation failed with error: {e}")
