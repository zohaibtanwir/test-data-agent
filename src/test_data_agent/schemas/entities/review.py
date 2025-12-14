"""Product review schema definition."""

REVIEW_SCHEMA = {
    "name": "review",
    "domain": "ecommerce",
    "description": "Product review from customer",
    "fields": {
        "review_id": {
            "type": "string",
            "format": "REV-{random:10}",
            "required": True,
            "description": "Unique review identifier",
        },
        "product_id": {
            "type": "string",
            "required": True,
            "description": "Product being reviewed",
        },
        "user_id": {
            "type": "string",
            "format": "USR-{random:7}",
            "required": True,
            "description": "User who wrote the review",
        },
        "rating": {
            "type": "integer",
            "min": 1,
            "max": 5,
            "required": True,
            "description": "Star rating (1-5)",
        },
        "title": {
            "type": "string",
            "min_length": 5,
            "max_length": 100,
            "required": True,
            "description": "Review title",
        },
        "body": {
            "type": "string",
            "min_length": 10,
            "max_length": 5000,
            "required": True,
            "description": "Review text",
        },
        "verified_purchase": {
            "type": "boolean",
            "default": False,
            "required": True,
            "description": "Whether reviewer purchased the product",
        },
        "helpful_votes": {
            "type": "integer",
            "min": 0,
            "default": 0,
            "required": True,
            "description": "Number of helpful votes",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Review creation timestamp",
        },
    },
    "coherence_rules": [
        "title and body should match rating sentiment",
    ],
}
