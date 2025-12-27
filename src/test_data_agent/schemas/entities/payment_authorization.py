"""Payment authorization schema definition."""

PAYMENT_AUTHORIZATION_SCHEMA = {
    "name": "payment_authorization",
    "domain": "ecommerce",
    "description": "Authorization for payment processing",
    "fields": {
        "auth_id": {
            "type": "string",
            "format": "AUTH-{year}-{random:7}",
            "required": True,
            "description": "Authorization identifier",
        },
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Associated order",
        },
        "amount": {
            "type": "float",
            "min": 0.01,
            "required": True,
            "description": "Authorized amount",
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
            "values": ["pending", "approved", "declined", "expired", "captured"],
            "default": "pending",
            "required": True,
            "description": "Authorization status",
        },
        "expires_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Authorization expiry",
        },
        "auth_code": {
            "type": "string",
            "required": False,
            "description": "Bank authorization code",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Authorization timestamp",
        },
    },
    "coherence_rules": [
        "Authorization expires after 7 days",
        "Cannot capture more than authorized amount",
    ],
}
