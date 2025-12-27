"""Shipping schema definition."""

SHIPPING_SCHEMA = {
    "name": "shipping",
    "domain": "ecommerce",
    "description": "Shipping and delivery information for orders",
    "fields": {
        "shipping_id": {
            "type": "string",
            "format": "SHIP-{year}-{random:7}",
            "required": True,
            "description": "Unique shipping identifier",
        },
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Associated order",
        },
        "carrier": {
            "type": "enum",
            "values": ["FedEx", "UPS", "USPS", "DHL", "Local"],
            "required": True,
            "description": "Shipping carrier",
        },
        "service_type": {
            "type": "enum",
            "values": ["standard", "express", "overnight", "same_day", "economy"],
            "default": "standard",
            "required": True,
            "description": "Shipping service level",
        },
        "tracking_number": {
            "type": "string",
            "required": True,
            "description": "Carrier tracking number",
        },
        "shipping_cost": {
            "type": "float",
            "min": 0,
            "required": True,
            "description": "Shipping cost",
        },
        "weight": {
            "type": "float",
            "min": 0.01,
            "required": True,
            "description": "Package weight in lbs",
        },
        "ship_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Shipment date",
        },
        "estimated_delivery": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Estimated delivery date",
        },
        "actual_delivery": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Actual delivery date",
        },
        "signature_required": {
            "type": "boolean",
            "default": False,
            "required": True,
            "description": "Signature required flag",
        },
        "status": {
            "type": "enum",
            "values": ["pending", "picked_up", "in_transit", "out_for_delivery", "delivered", "returned", "lost"],
            "default": "pending",
            "required": True,
            "description": "Shipping status",
        },
        "delivery_instructions": {
            "type": "string",
            "required": False,
            "description": "Special delivery instructions",
        },
    },
    "coherence_rules": [
        "Tracking number must be unique per carrier",
        "Cannot ship before order is paid",
    ],
}
