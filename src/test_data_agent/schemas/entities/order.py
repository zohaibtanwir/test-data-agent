"""Order schema definition."""

ORDER_SCHEMA = {
    "name": "order",
    "domain": "ecommerce",
    "description": "Customer order with items and shipping",
    "fields": {
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Unique order identifier",
        },
        "customer_id": {
            "type": "string",
            "format": "USR-{random:7}",
            "required": True,
            "description": "Customer who placed the order",
        },
        "items": {
            "type": "array",
            "required": True,
            "description": "Ordered items",
            "item_schema": {
                "type": "object",
                "fields": {
                    "sku": {"type": "string", "required": True},
                    "name": {"type": "string", "required": True},
                    "quantity": {"type": "integer", "min": 1, "required": True},
                    "price": {"type": "float", "min": 0.01, "required": True},
                },
            },
        },
        "shipping_address": {
            "type": "object",
            "required": True,
            "description": "Shipping address",
            "fields": {
                "street": {"type": "string", "required": True},
                "city": {"type": "string", "required": True},
                "state": {"type": "string", "required": True},
                "zip": {"type": "string", "required": True},
                "country": {"type": "string", "default": "US", "required": True},
            },
        },
        "billing_address": {
            "type": "object",
            "required": False,
            "description": "Billing address (optional, defaults to shipping)",
            "fields": {
                "street": {"type": "string", "required": True},
                "city": {"type": "string", "required": True},
                "state": {"type": "string", "required": True},
                "zip": {"type": "string", "required": True},
                "country": {"type": "string", "default": "US", "required": True},
            },
        },
        "payment_method": {
            "type": "enum",
            "values": ["credit_card", "paypal", "apple_pay", "google_pay", "gift_card"],
            "required": True,
            "description": "Payment method used",
        },
        "status": {
            "type": "enum",
            "values": ["pending", "confirmed", "shipped", "delivered", "cancelled"],
            "default": "pending",
            "required": True,
            "description": "Order status",
        },
        "subtotal": {"type": "float", "min": 0, "required": True},
        "tax": {"type": "float", "min": 0, "required": True},
        "shipping": {"type": "float", "min": 0, "required": True},
        "total": {"type": "float", "min": 0, "required": True},
        "created_at": {"type": "datetime", "format": "iso8601", "required": True},
        "updated_at": {"type": "datetime", "format": "iso8601", "required": False},
    },
    "coherence_rules": [
        "total = subtotal + tax + shipping",
        "updated_at >= created_at",
    ],
}
