"""Coupon schema definition."""

COUPON_SCHEMA = {
    "name": "coupon",
    "domain": "ecommerce",
    "description": "Coupon codes for discounts",
    "fields": {
        "coupon_id": {
            "type": "string",
            "format": "CPN-{year}-{random:7}",
            "required": True,
            "description": "Coupon identifier",
        },
        "code": {
            "type": "string",
            "required": True,
            "description": "Coupon code",
        },
        "discount_id": {
            "type": "string",
            "format": "DSC-{year}-{random:7}",
            "required": True,
            "description": "Associated discount",
        },
        "usage_limit": {
            "type": "integer",
            "min": 1,
            "required": True,
            "description": "Maximum total uses",
        },
        "usage_count": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Current usage count",
        },
        "per_customer_limit": {
            "type": "integer",
            "min": 1,
            "default": 1,
            "required": True,
            "description": "Uses per customer",
        },
        "valid_from": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Valid from date",
        },
        "valid_until": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Valid until date",
        },
        "status": {
            "type": "enum",
            "values": ["active", "exhausted", "expired", "disabled"],
            "default": "active",
            "required": True,
            "description": "Coupon status",
        },
    },
    "coherence_rules": [
        "Coupon code must be unique",
        "Cannot exceed usage limits",
    ],
}
