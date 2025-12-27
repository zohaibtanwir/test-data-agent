"""Subscription schema definition."""

SUBSCRIPTION_SCHEMA = {
    "name": "subscription",
    "domain": "ecommerce",
    "description": "Recurring subscription service",
    "fields": {
        "subscription_id": {
            "type": "string",
            "format": "SUB-{year}-{random:7}",
            "required": True,
            "description": "Subscription identifier",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Subscriber",
        },
        "product_id": {
            "type": "string",
            "format": "PRD-{random:7}",
            "required": True,
            "description": "Subscribed product",
        },
        "frequency": {
            "type": "enum",
            "values": ["weekly", "biweekly", "monthly", "quarterly", "yearly"],
            "required": True,
            "description": "Delivery frequency",
        },
        "quantity": {
            "type": "integer",
            "min": 1,
            "required": True,
            "description": "Quantity per delivery",
        },
        "price": {
            "type": "float",
            "min": 0.01,
            "required": True,
            "description": "Subscription price",
        },
        "next_delivery": {
            "type": "date",
            "format": "iso8601",
            "required": True,
            "description": "Next delivery date",
        },
        "status": {
            "type": "enum",
            "values": ["active", "paused", "cancelled", "expired"],
            "default": "active",
            "required": True,
            "description": "Subscription status",
        },
        "started_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Start date",
        },
        "cancelled_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Cancellation date",
        },
    },
    "coherence_rules": [
        "Payment method required for subscription",
        "3 failed payments triggers suspension",
    ],
}
