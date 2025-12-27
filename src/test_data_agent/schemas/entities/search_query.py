"""Search query schema definition."""

SEARCH_QUERY_SCHEMA = {
    "name": "search_query",
    "domain": "ecommerce",
    "description": "Customer search queries",
    "fields": {
        "query_id": {
            "type": "string",
            "format": "SQ-{year}-{random:7}",
            "required": True,
            "description": "Query identifier",
        },
        "query_text": {
            "type": "string",
            "required": True,
            "description": "Search query",
        },
        "customer_id": {
            "type": "string",
            "required": False,
            "description": "Searcher (if logged in)",
        },
        "session_id": {
            "type": "string",
            "required": True,
            "description": "Session identifier",
        },
        "results_count": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Number of results",
        },
        "clicked_products": {
            "type": "array",
            "required": False,
            "description": "Products clicked from results",
        },
        "filters_applied": {
            "type": "object",
            "required": False,
            "description": "Search filters applied",
        },
        "timestamp": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Search timestamp",
        },
    },
    "coherence_rules": [
        "Log all searches for analytics",
        "Personalize results for logged in users",
    ],
}
