"""Order item schema definition."""

ORDER_ITEM_SCHEMA = {
    "name": "order_item",
    "domain": "ecommerce",
    "description": "Individual item within an order",
    "fields": {
        "order_item_id": {
            "type": "string",
            "format": "OI-{year}-{random:7}",
            "required": True,
            "description": "Unique order item identifier",
        },
        "order_id": {
            "type": "string",
            "format": "ORD-{year}-{random:7}",
            "required": True,
            "description": "Parent order ID",
        },
        "product_id": {
            "type": "string",
            "format": "PRD-{random:7}",
            "required": True,
            "description": "Product identifier",
        },
        "sku": {
            "type": "string",
            "required": True,
            "description": "Stock keeping unit",
        },
        "quantity": {
            "type": "integer",
            "min": 1,
            "required": True,
            "description": "Ordered quantity",
        },
        "unit_price": {
            "type": "float",
            "min": 0.01,
            "required": True,
            "description": "Price per unit at time of order",
        },
        "total_price": {
            "type": "float",
            "min": 0.01,
            "required": True,
            "description": "Line item total",
        },
        "status": {
            "type": "enum",
            "values": ["pending", "shipped", "delivered", "returned"],
            "default": "pending",
            "required": True,
            "description": "Item status",
        },
    },
    "coherence_rules": [
        "total_price = quantity * unit_price",
        "Cannot modify after shipment",
    ],
}
