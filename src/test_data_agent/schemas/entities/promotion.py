"""Promotion schema definition."""

PROMOTION_SCHEMA = {
    "name": "promotion",
    "domain": "ecommerce",
    "description": "Promotional campaigns",
    "fields": {
        "promotion_id": {
            "type": "string",
            "format": "PRM-{year}-{random:7}",
            "required": True,
            "description": "Promotion identifier",
        },
        "name": {
            "type": "string",
            "required": True,
            "description": "Promotion name",
        },
        "description": {
            "type": "string",
            "required": True,
            "description": "Promotion description",
        },
        "type": {
            "type": "enum",
            "values": ["sale", "bundle", "flash", "loyalty"],
            "required": True,
            "description": "Promotion type",
        },
        "start_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Campaign start",
        },
        "end_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Campaign end",
        },
        "priority": {
            "type": "integer",
            "min": 1,
            "required": True,
            "description": "Priority for stacking",
        },
        "status": {
            "type": "enum",
            "values": ["draft", "active", "paused", "ended"],
            "default": "draft",
            "required": True,
            "description": "Promotion status",
        },
    },
    "coherence_rules": [
        "Only one flash sale active at a time",
        "Priority determines application order",
    ],
}
