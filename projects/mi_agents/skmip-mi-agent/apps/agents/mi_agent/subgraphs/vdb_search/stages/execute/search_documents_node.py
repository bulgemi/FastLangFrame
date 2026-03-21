from apps.agents.mi_agent.subgraphs.vdb_search.state import VDBSearchState
from apps.agents.mi_agent.tools.vdb_search_documents import search_documents_tool


async def search_documents_node(state: VDBSearchState) -> VDBSearchState:
    state.vector_sources = await search_documents_tool(state.authorized_product_nums, state.rewritten_query, state.repo_id)
    return state
