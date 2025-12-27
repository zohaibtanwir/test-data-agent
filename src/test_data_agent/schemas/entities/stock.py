"""Stock schema definition."""

STOCK_SCHEMA = {
    "name": "stock",
    "domain": "ecommerce",
    "description": "Current stock levels",
    "fields": {
        "stock_id": {
            "type": "string",
            "format": "STK-{year}-{random:7}",
            "required": True,
            "description": "Stock record identifier",
        },
        "sku": {
            "type": "string",
            "required": True,
            "description": "Stock keeping unit",
        },
        "location_id": {
            "type": "string",
            "required": True,
            "description": "Warehouse location",
        },
        "quantity": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Available quantity",
        },
        "reserved": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Reserved quantity",
        },
        "last_updated": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Last update timestamp",
        },
    },
    "coherence_rules": [
        "Quantity cannot be negative",
        "Reserved cannot exceed quantity",
    ],
}
