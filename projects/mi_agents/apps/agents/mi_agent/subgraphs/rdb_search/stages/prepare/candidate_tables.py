from apps.agents.mi_agent.subgraphs.rdb_search.schemas import RDBSearchCandidate
from apps.agents.mi_agent.subgraphs.rdb_search.state import RDBSearchState
from apps.agents.mi_agent.tools.rdb_search_candidates import retrieve_rdb_search_candidates


async def select_candidate_tables_node(state: RDBSearchState) -> RDBSearchState:
    cantidate_items: list[RDBSearchCandidate] = await retrieve_rdb_search_candidates(
        rdb_search_queries=state.rdb_search_queries,
        repo_id_rdb_metadata=state.repo_id_rdb_metadata,
        authorized_product_nums=state.authorized_product_nums,
        company_code=state.company_code,
    )
    state.cantidate_items = cantidate_items

    return state
