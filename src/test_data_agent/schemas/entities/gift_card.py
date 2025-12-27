"""Gift card schema definition."""

GIFT_CARD_SCHEMA = {
    "name": "gift_card",
    "domain": "ecommerce",
    "description": "Gift card purchase and redemption",
    "fields": {
        "gift_card_id": {
            "type": "string",
            "format": "GC-{year}-{random:7}",
            "required": True,
            "description": "Gift card identifier",
        },
        "code": {
            "type": "string",
            "required": True,
            "description": "Gift card code",
        },
        "initial_value": {
            "type": "float",
            "min": 10,
            "required": True,
            "description": "Original value",
        },
        "current_balance": {
            "type": "float",
            "min": 0,
            "required": True,
            "description": "Current balance",
        },
        "currency": {
            "type": "enum",
            "values": ["USD", "CAD", "EUR", "GBP"],
            "default": "USD",
            "required": True,
            "description": "Currency",
        },
        "purchaser_id": {
            "type": "string",
            "required": False,
            "description": "Purchaser customer ID",
        },
        "recipient_email": {
            "type": "string",
            "required": False,
            "description": "Recipient email",
        },
        "expires_at": {
            "type": "date",
            "format": "iso8601",
            "required": False,
            "description": "Expiration date",
        },
        "status": {
            "type": "enum",
            "values": ["active", "redeemed", "expired", "cancelled"],
            "default": "active",
            "required": True,
            "description": "Gift card status",
        },
        "purchased_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Purchase date",
        },
    },
    "coherence_rules": [
        "Gift card codes must be unique",
        "Cannot reload physical gift cards",
        "Minimum purchase amount $10",
    ],
}
