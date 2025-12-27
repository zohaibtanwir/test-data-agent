"""Stock alert schema definition."""

STOCK_ALERT_SCHEMA = {
    "name": "stock_alert",
    "domain": "ecommerce",
    "description": "Low stock notifications",
    "fields": {
        "alert_id": {
            "type": "string",
            "format": "SA-{year}-{random:7}",
            "required": True,
            "description": "Alert identifier",
        },
        "sku": {
            "type": "string",
            "required": True,
            "description": "Stock keeping unit",
        },
        "threshold": {
            "type": "integer",
            "min": 1,
            "required": True,
            "description": "Alert threshold",
        },
        "current_level": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Current stock level",
        },
        "triggered_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Alert trigger time",
        },
        "status": {
            "type": "enum",
            "values": ["active", "acknowledged", "resolved"],
            "default": "active",
            "required": True,
            "description": "Alert status",
        },
    },
    "coherence_rules": [
        "Alert when stock falls below threshold",
        "One active alert per SKU",
    ],
}
