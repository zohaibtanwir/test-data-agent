"""Shipment schema definition."""

SHIPMENT_SCHEMA = {
    "name": "shipment",
    "domain": "ecommerce",
    "description": "Individual shipment tracking",
    "fields": {
        "shipment_id": {
            "type": "string",
            "format": "SHP-{year}-{random:7}",
            "required": True,
            "description": "Shipment identifier",
        },
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Parent order ID",
        },
        "package_count": {
            "type": "integer",
            "min": 1,
            "required": True,
            "description": "Number of packages",
        },
        "carrier": {
            "type": "enum",
            "values": ["FedEx", "UPS", "USPS", "DHL", "Local"],
            "required": True,
            "description": "Shipping carrier",
        },
        "tracking_number": {
            "type": "string",
            "required": True,
            "description": "Tracking number",
        },
        "ship_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Ship date",
        },
        "delivery_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Delivery date",
        },
        "status": {
            "type": "enum",
            "values": ["preparing", "shipped", "in_transit", "delivered", "returned"],
            "default": "preparing",
            "required": True,
            "description": "Shipment status",
        },
        "items": {
            "type": "array",
            "required": True,
            "description": "Items in shipment",
        },
    },
    "coherence_rules": [
        "Each package must have tracking",
        "Cannot ship cancelled items",
    ],
}
