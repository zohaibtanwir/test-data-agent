"""Return request schema definition."""

RETURN_SCHEMA = {
    "name": "return",
    "domain": "ecommerce",
    "description": "Product return request",
    "fields": {
        "return_id": {
            "type": "string",
            "format": "RET-{year}-{random:7}",
            "required": True,
            "description": "Return identifier",
        },
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Original order",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Customer ID",
        },
        "items": {
            "type": "array",
            "required": True,
            "description": "Items being returned",
        },
        "reason": {
            "type": "enum",
            "values": ["defective", "wrong_item", "not_as_described", "changed_mind", "other"],
            "required": True,
            "description": "Return reason",
        },
        "status": {
            "type": "enum",
            "values": ["requested", "approved", "rejected", "received", "refunded"],
            "default": "requested",
            "required": True,
            "description": "Return status",
        },
        "return_label": {
            "type": "string",
            "required": False,
            "description": "Return shipping label",
        },
        "refund_amount": {
            "type": "float",
            "min": 0,
            "required": True,
            "description": "Refund amount",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Request date",
        },
        "processed_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Processing date",
        },
    },
    "coherence_rules": [
        "Return within 30 days of delivery",
        "Some items are final sale",
    ],
}
