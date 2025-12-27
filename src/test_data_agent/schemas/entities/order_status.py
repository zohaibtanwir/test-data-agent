"""Order status schema definition."""

ORDER_STATUS_SCHEMA = {
    "name": "order_status",
    "domain": "ecommerce",
    "description": "Status tracking for orders",
    "fields": {
        "status_id": {
            "type": "string",
            "format": "OS-{year}-{random:7}",
            "required": True,
            "description": "Unique status record identifier",
        },
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Associated order",
        },
        "status": {
            "type": "enum",
            "values": ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"],
            "required": True,
            "description": "Order status value",
        },
        "timestamp": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Status change time",
        },
        "notes": {
            "type": "string",
            "required": False,
            "description": "Status notes",
        },
        "updated_by": {
            "type": "string",
            "required": False,
            "description": "User or system that made the change",
        },
    },
    "coherence_rules": [
        "Status changes must follow valid transitions",
        "Cannot revert to previous status",
    ],
}
