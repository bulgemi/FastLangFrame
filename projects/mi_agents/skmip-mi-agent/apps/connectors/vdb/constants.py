AX_PLATFORM_ADVANCED_QUERY_URI = "/api/v1/knowledge/queries/advanced"
INDEX_FIELDS = {
    "contributor": "string",
    "language": "string",
    "document_release_date": "datetime",
    "gds_no": "string",
    "gds_data_dstg_id": "string",
    "document_id": "string",
}


FIELD_DESCRIPTIONS = {
    "contributor": "문서를 집필한 사람",
    "language": "언어",
    "document_release_date": "문서 발행일",
    "gds_no": "GDS 번호",
    "document_id": "gds_data_dstg_id",
}

FILTERABLE_FIELDS = [
    "contributor",
    "language",
    "document_release_date",
    "gds_no",
    "document_id",
]
SORTABLE_FIELDS = ["document_release_date"]
