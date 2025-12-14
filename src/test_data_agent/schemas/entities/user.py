"""User/Customer schema definition."""

USER_SCHEMA = {
    "name": "user",
    "domain": "ecommerce",
    "description": "Customer/user account",
    "fields": {
        "user_id": {
            "type": "string",
            "format": "USR-{random:7}",
            "required": True,
            "description": "Unique user identifier",
        },
        "email": {
            "type": "email",
            "required": True,
            "description": "User email address",
        },
        "first_name": {
            "type": "string",
            "min_length": 1,
            "max_length": 50,
            "required": True,
            "description": "First name",
        },
        "last_name": {
            "type": "string",
            "min_length": 1,
            "max_length": 50,
            "required": True,
            "description": "Last name",
        },
        "phone": {
            "type": "phone",
            "required": False,
            "description": "Phone number",
        },
        "addresses": {
            "type": "array",
            "required": False,
            "description": "Saved addresses",
            "item_schema": {
                "type": "object",
                "fields": {
                    "label": {"type": "string", "required": False, "description": "Address label (home, work, etc.)"},
                    "street": {"type": "string", "required": True},
                    "city": {"type": "string", "required": True},
                    "state": {"type": "string", "required": True},
                    "zip": {"type": "string", "required": True},
                    "country": {"type": "string", "default": "US", "required": True},
                    "is_default": {"type": "boolean", "default": False, "required": False},
                },
            },
        },
        "loyalty_tier": {
            "type": "enum",
            "values": ["bronze", "silver", "gold", "platinum"],
            "default": "bronze",
            "required": False,
            "description": "Star Rewards loyalty tier",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Account creation timestamp",
        },
        "last_login": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Last login timestamp",
        },
    },
    "coherence_rules": [
        "last_login >= created_at if last_login exists",
    ],
}
