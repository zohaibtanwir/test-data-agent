"""Tracking schema definition."""

TRACKING_SCHEMA = {
    "name": "tracking",
    "domain": "ecommerce",
    "description": "Package tracking information",
    "fields": {
        "tracking_id": {
            "type": "string",
            "format": "TRK-{year}-{random:7}",
            "required": True,
            "description": "Tracking event ID",
        },
        "shipment_id": {
            "type": "string",
            "format": "SHP-{year}-{random:7}",
            "required": True,
            "description": "Parent shipment",
        },
        "tracking_number": {
            "type": "string",
            "required": True,
            "description": "Carrier tracking number",
        },
        "status": {
            "type": "string",
            "required": True,
            "description": "Tracking status",
        },
        "location": {
            "type": "string",
            "required": True,
            "description": "Current location",
        },
        "timestamp": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Event timestamp",
        },
        "description": {
            "type": "string",
            "required": True,
            "description": "Event description",
        },
    },
    "coherence_rules": [
        "Events must be chronologically ordered",
        "Location required for transit events",
    ],
}
