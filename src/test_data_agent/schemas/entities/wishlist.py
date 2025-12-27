"""Wishlist schema definition."""

WISHLIST_SCHEMA = {
    "name": "wishlist",
    "domain": "ecommerce",
    "description": "Customer's saved items for later",
    "fields": {
        "wishlist_id": {
            "type": "string",
            "format": "WL-{year}-{random:7}",
            "required": True,
            "description": "Wishlist identifier",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Wishlist owner",
        },
        "name": {
            "type": "string",
            "required": True,
            "description": "Wishlist name",
        },
        "items": {
            "type": "array",
            "required": True,
            "description": "Wishlist items",
        },
        "is_public": {
            "type": "boolean",
            "default": False,
            "required": True,
            "description": "Public visibility",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Creation date",
        },
        "updated_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Last update date",
        },
    },
    "coherence_rules": [
        "Maximum 5 wishlists per customer",
        "Maximum 100 items per wishlist",
    ],
}
