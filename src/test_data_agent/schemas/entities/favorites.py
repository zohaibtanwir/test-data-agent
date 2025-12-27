"""Favorites schema definition."""

FAVORITES_SCHEMA = {
    "name": "favorites",
    "domain": "ecommerce",
    "description": "Customer's favorite products",
    "fields": {
        "favorite_id": {
            "type": "string",
            "format": "FAV-{year}-{random:7}",
            "required": True,
            "description": "Favorite identifier",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Customer ID",
        },
        "product_id": {
            "type": "string",
            "format": "PRD-{random:7}",
            "required": True,
            "description": "Favorited product",
        },
        "added_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Date added",
        },
        "notes": {
            "type": "string",
            "required": False,
            "description": "Personal notes",
        },
    },
    "coherence_rules": [
        "No duplicate favorites per customer",
        "Maximum 500 favorites",
    ],
}
