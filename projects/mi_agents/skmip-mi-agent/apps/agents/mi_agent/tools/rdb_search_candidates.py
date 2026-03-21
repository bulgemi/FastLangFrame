from __future__ import annotations

from uuid import UUID

from apps.agents.mi_agent.subgraphs.rdb_search.schemas import RDBSearchCandidate, RDBSearchQuery, VDBSearchCandidate
from apps.connectors.vdb.enums import RetrievalMode
from apps.connectors.vdb.schemas import RetrievalResult
from apps.connectors.vdb.vector_db import AipKnowledgeRetriever


async def retrieve_rdb_search_candidates(
    rdb_search_queries: list[RDBSearchQuery],
    repo_id_rdb_metadata: str,
    authorized_product_nums: list[int] | None,
    company_code: str | None,
) -> list[RDBSearchCandidate]:
    return await _retrieve_candidate_data(
        rdb_search_queries=rdb_search_queries,
        repo_id_rdb_metadata=repo_id_rdb_metadata,
        authorized_product_nums=authorized_product_nums,
        company_code=company_code,
    )


async def _retrieve_candidate_data(
    rdb_search_queries: list[RDBSearchQuery],
    repo_id_rdb_metadata: UUID,
    authorized_product_nums: list[int] | None,
    company_code: str | None,
) -> list[RDBSearchCandidate]:
    retriever = AipKnowledgeRetriever()
    rdb_search_candidates: list[RDBSearchCandidate] = []
    if authorized_product_nums is not None and len(authorized_product_nums) == 0:
        return rdb_search_candidates

    filter_expr: str = "src_del_yn eq 'N' and del_yn eq 'N'"
    if authorized_product_nums:
        nums = ", ".join(str(num) for num in authorized_product_nums)
        filter_expr += f" and gds_no in [{nums}]"

    for rdb_search_query in rdb_search_queries:
        rewrite_query: str = rdb_search_query.query
        query_text: str = rdb_search_query.search_text

        retrieval_results:  list[RetrievalResult] = await retriever.retrieve(
            repo_id=repo_id_rdb_metadata,
            query=rewrite_query,
            retrieval_mode=RetrievalMode.SPARSE,
            top_k=10,
            query_keywords=query_text,
            text_search_fields=["content", "keywords"],
            filter_expn=filter_expr,
        )
        vdb_candidates: list[VDBSearchCandidate] = []

        for item in retrieval_results:
            metadata = item.metadata

            vdb_candidate = VDBSearchCandidate(
                tbl_expn=item.content,
                agtmtm_id=metadata.get("agtmtm_id"),
            )
            vdb_candidates.append(vdb_candidate)

        rdb_search_candidate: RDBSearchCandidate = RDBSearchCandidate(
            query=rewrite_query,
            company_code=company_code,
            vdb_search_candidates=vdb_candidates,
        )
        rdb_search_candidates.append(rdb_search_candidate)

    return rdb_search_candidates
