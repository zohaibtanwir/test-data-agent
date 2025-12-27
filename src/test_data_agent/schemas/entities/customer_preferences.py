"""Customer preferences schema definition."""

CUSTOMER_PREFERENCES_SCHEMA = {
    "name": "customer_preferences",
    "domain": "ecommerce",
    "description": "Customer shopping preferences",
    "fields": {
        "preference_id": {
            "type": "string",
            "format": "CP-{year}-{random:7}",
            "required": True,
            "description": "Preference record ID",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Customer ID",
        },
        "preferred_categories": {
            "type": "array",
            "required": False,
            "description": "Preferred product categories",
        },
        "communication_channels": {
            "type": "array",
            "required": True,
            "description": "Preferred contact methods",
        },
        "language": {
            "type": "string",
            "default": "en-US",
            "required": True,
            "description": "Language preference",
        },
        "currency": {
            "type": "enum",
            "values": ["USD", "CAD", "EUR", "GBP"],
            "default": "USD",
            "required": True,
            "description": "Currency preference",
        },
        "timezone": {
            "type": "string",
            "default": "America/New_York",
            "required": False,
            "description": "Timezone preference",
        },
        "updated_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Last update timestamp",
        },
    },
    "coherence_rules": [
        "At least one communication channel required",
        "Preferences sync across devices",
    ],
}
