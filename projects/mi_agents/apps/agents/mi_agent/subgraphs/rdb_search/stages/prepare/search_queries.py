from apps.agents.mi_agent.subgraphs.rdb_search.schemas import RDBSearchQuery
from apps.agents.mi_agent.subgraphs.rdb_search.state import RDBSearchState
from apps.agents.mi_agent.tools.rdb_search_queries import prepare_rdb_search_queries


async def prepare_rdb_search_queries_node(
    state: RDBSearchState,
) -> list[RDBSearchQuery]:
    state.rdb_search_queries = prepare_rdb_search_queries(state.rewritten_query)
    return state
