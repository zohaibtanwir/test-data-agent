"""Discount schema definition."""

DISCOUNT_SCHEMA = {
    "name": "discount",
    "domain": "ecommerce",
    "description": "Discount rules and applications",
    "fields": {
        "discount_id": {
            "type": "string",
            "format": "DSC-{year}-{random:7}",
            "required": True,
            "description": "Discount identifier",
        },
        "name": {
            "type": "string",
            "required": True,
            "description": "Discount name",
        },
        "type": {
            "type": "enum",
            "values": ["percentage", "fixed", "bogo"],
            "required": True,
            "description": "Discount type",
        },
        "value": {
            "type": "float",
            "min": 0,
            "required": True,
            "description": "Discount value",
        },
        "min_purchase": {
            "type": "float",
            "min": 0,
            "required": False,
            "description": "Minimum purchase amount",
        },
        "max_discount": {
            "type": "float",
            "min": 0,
            "required": False,
            "description": "Maximum discount cap",
        },
        "start_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Start date",
        },
        "end_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "End date",
        },
        "status": {
            "type": "enum",
            "values": ["active", "inactive", "expired"],
            "default": "active",
            "required": True,
            "description": "Discount status",
        },
    },
    "coherence_rules": [
        "End date must be after start date",
        "Discount cannot exceed item price",
    ],
}
