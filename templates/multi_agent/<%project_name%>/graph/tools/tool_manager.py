from langchain_core.tools import tool

@tool
def researcher_tool(query: str) -> str:
    """Useful for researching a topic."""
    return f"Research results for {query}"

@tool
def writer_tool(topic: str) -> str:
    """Useful for writing content about a topic."""
    return f"Written content about {topic}"
