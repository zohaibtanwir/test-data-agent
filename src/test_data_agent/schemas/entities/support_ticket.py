"""Support ticket schema definition."""

SUPPORT_TICKET_SCHEMA = {
    "name": "support_ticket",
    "domain": "ecommerce",
    "description": "Customer support requests",
    "fields": {
        "ticket_id": {
            "type": "string",
            "format": "TKT-{year}-{random:7}",
            "required": True,
            "description": "Ticket identifier",
        },
        "customer_id": {
            "type": "string",
            "format": "CUST-{year}-{random:7}",
            "required": True,
            "description": "Customer",
        },
        "order_id": {
            "type": "string",
            "required": False,
            "description": "Related order",
        },
        "category": {
            "type": "enum",
            "values": ["order", "shipping", "product", "account", "payment", "other"],
            "required": True,
            "description": "Ticket category",
        },
        "subject": {
            "type": "string",
            "required": True,
            "description": "Ticket subject",
        },
        "description": {
            "type": "string",
            "required": True,
            "description": "Issue description",
        },
        "priority": {
            "type": "enum",
            "values": ["low", "medium", "high", "urgent"],
            "default": "medium",
            "required": True,
            "description": "Ticket priority",
        },
        "status": {
            "type": "enum",
            "values": ["open", "in_progress", "waiting_customer", "resolved", "closed"],
            "default": "open",
            "required": True,
            "description": "Ticket status",
        },
        "assigned_to": {
            "type": "string",
            "required": False,
            "description": "Assigned agent",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Creation date",
        },
        "resolved_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Resolution date",
        },
    },
    "coherence_rules": [
        "Urgent tickets must be responded within 1 hour",
        "Auto-escalate unresponsed tickets after 24 hours",
    ],
}
