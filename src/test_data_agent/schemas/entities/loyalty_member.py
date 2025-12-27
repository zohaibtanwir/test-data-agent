"""Loyalty member schema definition."""

LOYALTY_MEMBER_SCHEMA = {
    "name": "loyalty_member",
    "domain": "ecommerce",
    "description": "Loyalty program membership",
    "fields": {
        "member_id": {
            "type": "string",
            "format": "LM-{year}-{random:7}",
            "required": True,
            "description": "Membership identifier",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Customer ID",
        },
        "tier": {
            "type": "enum",
            "values": ["bronze", "silver", "gold", "platinum"],
            "default": "bronze",
            "required": True,
            "description": "Membership tier",
        },
        "points_balance": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Current points",
        },
        "points_earned_ytd": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Points earned this year",
        },
        "tier_expiry": {
            "type": "date",
            "format": "iso8601",
            "required": True,
            "description": "Tier expiration date",
        },
        "enrolled_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Enrollment date",
        },
        "status": {
            "type": "enum",
            "values": ["active", "suspended", "expired"],
            "default": "active",
            "required": True,
            "description": "Membership status",
        },
    },
    "coherence_rules": [
        "Tier upgrade based on points threshold",
        "Points expire after 12 months of inactivity",
    ],
}
