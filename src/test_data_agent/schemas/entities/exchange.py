"""Exchange schema definition."""

EXCHANGE_SCHEMA = {
    "name": "exchange",
    "domain": "ecommerce",
    "description": "Product exchange request",
    "fields": {
        "exchange_id": {
            "type": "string",
            "format": "EXC-{year}-{random:7}",
            "required": True,
            "description": "Exchange identifier",
        },
        "return_id": {
            "type": "string",
            "format": "RET-{year}-{random:7}",
            "required": True,
            "description": "Associated return",
        },
        "original_item": {
            "type": "object",
            "required": True,
            "description": "Original item details",
        },
        "new_item": {
            "type": "object",
            "required": True,
            "description": "Replacement item details",
        },
        "price_difference": {
            "type": "float",
            "required": True,
            "description": "Price difference (positive = upcharge)",
        },
        "status": {
            "type": "enum",
            "values": ["pending", "approved", "shipped", "completed", "cancelled"],
            "default": "pending",
            "required": True,
            "description": "Exchange status",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Request date",
        },
        "completed_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Completion date",
        },
    },
    "coherence_rules": [
        "Exchange item must be available",
        "Price difference charged or refunded",
    ],
}
