"""Customer schema definition."""

CUSTOMER_SCHEMA = {
    "name": "customer",
    "domain": "ecommerce",
    "description": "Customer profile and account information",
    "fields": {
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Unique customer identifier",
        },
        "email": {
            "type": "string",
            "required": True,
            "description": "Customer email address",
        },
        "first_name": {
            "type": "string",
            "required": True,
            "description": "Customer first name",
        },
        "last_name": {
            "type": "string",
            "required": True,
            "description": "Customer last name",
        },
        "phone": {
            "type": "string",
            "required": False,
            "description": "Phone number",
        },
        "date_of_birth": {
            "type": "date",
            "format": "iso8601",
            "required": False,
            "description": "Date of birth",
        },
        "loyalty_tier": {
            "type": "enum",
            "values": ["bronze", "silver", "gold", "platinum", "vip"],
            "default": "bronze",
            "required": True,
            "description": "Loyalty program tier",
        },
        "loyalty_points": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Current loyalty points",
        },
        "lifetime_value": {
            "type": "float",
            "min": 0,
            "required": True,
            "description": "Total lifetime purchase value",
        },
        "registration_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Account creation date",
        },
        "last_login": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Last login timestamp",
        },
        "preferred_language": {
            "type": "string",
            "default": "en-US",
            "required": False,
            "description": "Language preference",
        },
        "marketing_consent": {
            "type": "boolean",
            "default": False,
            "required": True,
            "description": "Email marketing consent",
        },
        "account_status": {
            "type": "enum",
            "values": ["active", "suspended", "closed", "pending_verification"],
            "default": "active",
            "required": True,
            "description": "Account status",
        },
    },
    "coherence_rules": [
        "Email must be unique across customers",
        "Loyalty tier based on lifetime value or points",
    ],
}
