from langchain_core.tools import tool
from src.utils.connectors.db.db_client import DBClient
from src.utils.connectors.vdb.vector_db import VectorDBClient

@tool
def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is sunny and 25°C."

@tool
async def query_db(query: str) -> str:
    """Query the relational database for structured information."""
    db = DBClient()
    # In a real scenario, you would use db.get_session() to execute SQL
    return f"DB Query results for: {query}. (Mocked response from SQLAlchemy connector)"

@tool
async def vector_search(query: str) -> str:
    """Search for semantically similar documents in the vector database (Opensearch)."""
    vdb = VectorDBClient()
    results = await vdb.search(index="agent_docs", query=query)
    return f"Vector search results for '{query}': {results} (Mocked response from VDB connector)"

tools = [get_weather, query_db, vector_search]
