"""Fraud check schema definition."""

FRAUD_CHECK_SCHEMA = {
    "name": "fraud_check",
    "domain": "ecommerce",
    "description": "Fraud detection and prevention",
    "fields": {
        "check_id": {
            "type": "string",
            "format": "FC-{year}-{random:7}",
            "required": True,
            "description": "Check identifier",
        },
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Order being checked",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Customer",
        },
        "risk_score": {
            "type": "float",
            "min": 0,
            "max": 100,
            "required": True,
            "description": "Risk score 0-100",
        },
        "signals": {
            "type": "array",
            "required": True,
            "description": "Risk signals detected",
        },
        "decision": {
            "type": "enum",
            "values": ["approve", "review", "decline"],
            "required": True,
            "description": "Decision",
        },
        "reviewed_by": {
            "type": "string",
            "required": False,
            "description": "Manual reviewer ID",
        },
        "timestamp": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Check timestamp",
        },
        "notes": {
            "type": "string",
            "required": False,
            "description": "Review notes",
        },
    },
    "coherence_rules": [
        "Orders above $500 require additional verification",
        "New customers have elevated scrutiny",
    ],
}
