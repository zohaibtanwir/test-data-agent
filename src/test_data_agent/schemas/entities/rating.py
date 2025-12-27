"""Rating schema definition."""

RATING_SCHEMA = {
    "name": "rating",
    "domain": "ecommerce",
    "description": "Product rating scores",
    "fields": {
        "rating_id": {
            "type": "string",
            "format": "RAT-{year}-{random:7}",
            "required": True,
            "description": "Rating identifier",
        },
        "product_id": {
            "type": "string",
            "format": "PRD-{random:7}",
            "required": True,
            "description": "Rated product",
        },
        "average_rating": {
            "type": "float",
            "min": 0,
            "max": 5,
            "required": True,
            "description": "Average rating",
        },
        "total_reviews": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Total review count",
        },
        "rating_distribution": {
            "type": "object",
            "required": True,
            "description": "Distribution by stars",
        },
        "last_updated": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Last calculation time",
        },
    },
    "coherence_rules": [
        "Rating recalculated on new review",
        "Minimum 5 reviews for display",
    ],
}
