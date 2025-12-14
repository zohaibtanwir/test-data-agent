"""Payment schema definition."""

PAYMENT_SCHEMA = {
    "name": "payment",
    "domain": "ecommerce",
    "description": "Payment transaction record",
    "fields": {
        "payment_id": {
            "type": "string",
            "format": "PAY-{year}-{random:7}",
            "required": True,
            "description": "Unique payment identifier",
        },
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Associated order ID",
        },
        "method": {
            "type": "enum",
            "values": ["credit_card", "debit_card", "paypal", "apple_pay", "google_pay", "gift_card"],
            "required": True,
            "description": "Payment method",
        },
        "amount": {
            "type": "float",
            "min": 0.01,
            "required": True,
            "description": "Payment amount",
        },
        "currency": {
            "type": "enum",
            "values": ["USD", "CAD", "EUR", "GBP"],
            "default": "USD",
            "required": True,
            "description": "Currency code",
        },
        "status": {
            "type": "enum",
            "values": ["pending", "authorized", "captured", "failed", "refunded"],
            "default": "pending",
            "required": True,
            "description": "Payment status",
        },
        "card_last_four": {
            "type": "string",
            "pattern": "^[0-9]{4}$",
            "required": False,
            "description": "Last 4 digits of card (if applicable)",
        },
        "transaction_id": {
            "type": "string",
            "required": False,
            "description": "External transaction ID",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Payment creation timestamp",
        },
        "authorized_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Authorization timestamp",
        },
        "captured_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Capture timestamp",
        },
    },
    "coherence_rules": [
        "authorized_at >= created_at if authorized_at exists",
        "captured_at >= authorized_at if captured_at exists",
    ],
}
