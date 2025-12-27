"""Analytics event schema definition."""

ANALYTICS_EVENT_SCHEMA = {
    "name": "analytics_event",
    "domain": "ecommerce",
    "description": "User behavior tracking events",
    "fields": {
        "event_id": {
            "type": "string",
            "format": "EVT-{year}-{random:7}",
            "required": True,
            "description": "Event identifier",
        },
        "event_type": {
            "type": "enum",
            "values": [
                "page_view",
                "product_view",
                "add_to_cart",
                "checkout",
                "purchase",
                "search",
            ],
            "required": True,
            "description": "Event type",
        },
        "customer_id": {
            "type": "string",
            "required": False,
            "description": "Customer ID (if logged in)",
        },
        "session_id": {
            "type": "string",
            "required": True,
            "description": "Session identifier",
        },
        "product_id": {
            "type": "string",
            "required": False,
            "description": "Related product",
        },
        "metadata": {
            "type": "object",
            "required": False,
            "description": "Event metadata",
        },
        "timestamp": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Event timestamp",
        },
        "user_agent": {
            "type": "string",
            "required": False,
            "description": "Browser user agent",
        },
        "ip_address": {
            "type": "string",
            "required": False,
            "description": "Client IP address",
        },
    },
    "coherence_rules": [
        "Events anonymized after 90 days",
        "Session expires after 30 minutes inactivity",
    ],
}
