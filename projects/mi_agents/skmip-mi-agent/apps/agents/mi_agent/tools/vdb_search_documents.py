import json

from apps.connectors.vdb.schemas import RetrievalResult
from apps.connectors.vdb.vector_db import AipKnowledgeRetriever


async def search_documents_tool(
    authorized_product_nums: list[int],
    rewritten_query: str,
    repo_id: str,
) -> list:
    authorized_product_nums: list[int] | None = authorized_product_nums
    if authorized_product_nums is not None and len(authorized_product_nums) == 0:
        return []

    filter_expr: str | None = None
    if authorized_product_nums:
        nums = ", ".join(str(num) for num in authorized_product_nums)
        filter_expr = f"gds_no in [{nums}]"

    retriever = AipKnowledgeRetriever()
    message = rewritten_query
    retrieval_results: list[RetrievalResult] = await retriever.retrieve(
        repo_id=repo_id,
        query=message,
        top_k=3,
        filter_expn=filter_expr,
    )

    if retrieval_results:
        vector_metadata = []
        for doc in retrieval_results:
            metadata = doc.metadata
            vector_metadata.append(
                {
                    "source": metadata.get(
                        "contributor",
                        metadata.get("source", {}),
                    ),
                    "title": metadata.get("headline"),
                    "gds_no": metadata.get("gds_no"),
                    "gds_data_dstg_id": str(metadata.get("document_id", "")),
                },
            )

        retrieval_results = list(
            {json.dumps(item, sort_keys=True): item for item in vector_metadata}.values(),
        )
    return retrieval_results
