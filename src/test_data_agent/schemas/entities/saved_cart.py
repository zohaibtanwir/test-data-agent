"""Saved cart schema definition."""

SAVED_CART_SCHEMA = {
    "name": "saved_cart",
    "domain": "ecommerce",
    "description": "Cart saved for later purchase",
    "fields": {
        "saved_cart_id": {
            "type": "string",
            "format": "SC-{year}-{random:7}",
            "required": True,
            "description": "Unique saved cart identifier",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Customer who saved the cart",
        },
        "name": {
            "type": "string",
            "required": True,
            "description": "User-defined cart name",
        },
        "items": {
            "type": "array",
            "required": True,
            "description": "List of saved items",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Save date",
        },
        "expires_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Expiration date",
        },
        "status": {
            "type": "enum",
            "values": ["active", "expired", "converted"],
            "default": "active",
            "required": True,
            "description": "Cart status",
        },
    },
    "coherence_rules": [
        "Saved carts expire after 90 days",
        "Maximum 10 saved carts per customer",
    ],
}
