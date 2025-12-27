"""Refund schema definition."""

REFUND_SCHEMA = {
    "name": "refund",
    "domain": "ecommerce",
    "description": "Refund transaction for returned items",
    "fields": {
        "refund_id": {
            "type": "string",
            "format": "REF-{year}-{random:7}",
            "required": True,
            "description": "Unique refund identifier",
        },
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Original order ID",
        },
        "payment_id": {
            "type": "string",
            "format": "PAY-{year}-{random:7}",
            "required": True,
            "description": "Original payment ID",
        },
        "amount": {
            "type": "float",
            "min": 0.01,
            "required": True,
            "description": "Refund amount",
        },
        "currency": {
            "type": "enum",
            "values": ["USD", "CAD", "EUR", "GBP"],
            "default": "USD",
            "required": True,
            "description": "Currency code",
        },
        "reason": {
            "type": "string",
            "required": True,
            "description": "Refund reason",
        },
        "status": {
            "type": "enum",
            "values": ["pending", "processing", "processed", "failed"],
            "default": "pending",
            "required": True,
            "description": "Refund status",
        },
        "processed_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Processing timestamp",
        },
        "gateway_reference": {
            "type": "string",
            "required": False,
            "description": "Payment gateway refund ID",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Refund request timestamp",
        },
    },
    "coherence_rules": [
        "Refund cannot exceed original payment",
        "Refund must be processed within 5 business days",
    ],
}
