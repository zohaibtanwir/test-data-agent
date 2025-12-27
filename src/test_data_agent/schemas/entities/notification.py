"""Notification schema definition."""

NOTIFICATION_SCHEMA = {
    "name": "notification",
    "domain": "ecommerce",
    "description": "Customer notifications",
    "fields": {
        "notification_id": {
            "type": "string",
            "format": "NOT-{year}-{random:7}",
            "required": True,
            "description": "Notification identifier",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Recipient",
        },
        "type": {
            "type": "enum",
            "values": ["order", "shipping", "promotion", "alert", "account"],
            "required": True,
            "description": "Notification type",
        },
        "channel": {
            "type": "enum",
            "values": ["email", "sms", "push", "in_app"],
            "required": True,
            "description": "Delivery channel",
        },
        "subject": {
            "type": "string",
            "required": True,
            "description": "Notification subject",
        },
        "content": {
            "type": "string",
            "required": True,
            "description": "Notification content",
        },
        "status": {
            "type": "enum",
            "values": ["pending", "sent", "delivered", "failed", "read"],
            "default": "pending",
            "required": True,
            "description": "Delivery status",
        },
        "sent_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Send timestamp",
        },
        "read_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Read timestamp",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Creation timestamp",
        },
    },
    "coherence_rules": [
        "Respect customer communication preferences",
        "Rate limit per channel per customer",
    ],
}
