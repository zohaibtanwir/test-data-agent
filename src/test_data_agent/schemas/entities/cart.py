"""Shopping cart schema definition."""

CART_SCHEMA = {
    "name": "cart",
    "domain": "ecommerce",
    "description": "Shopping cart with items",
    "fields": {
        "cart_id": {
            "type": "string",
            "format": "CRT-{year}-{random:7}",
            "required": True,
            "description": "Unique cart identifier",
        },
        "customer_id": {
            "type": "string",
            "format": "USR-{random:7}",
            "required": True,
            "description": "Customer who owns the cart",
        },
        "items": {
            "type": "array",
            "required": True,
            "description": "Items in the cart",
            "item_schema": {
                "type": "object",
                "fields": {
                    "sku": {
                        "type": "string",
                        "required": True,
                        "description": "Product SKU",
                    },
                    "name": {
                        "type": "string",
                        "required": True,
                        "description": "Product name",
                    },
                    "quantity": {
                        "type": "integer",
                        "min": 1,
                        "max": 99,
                        "required": True,
                        "description": "Quantity",
                    },
                    "price": {
                        "type": "float",
                        "min": 0.01,
                        "required": True,
                        "description": "Unit price",
                    },
                    "category": {
                        "type": "string",
                        "required": False,
                        "description": "Product category",
                    },
                },
            },
        },
        "subtotal": {
            "type": "float",
            "min": 0,
            "required": True,
            "description": "Subtotal before tax",
        },
        "tax": {
            "type": "float",
            "min": 0,
            "required": True,
            "description": "Tax amount",
        },
        "total": {
            "type": "float",
            "min": 0,
            "required": True,
            "description": "Total including tax",
        },
        "currency": {
            "type": "enum",
            "values": ["USD", "CAD"],
            "default": "USD",
            "required": False,
            "description": "Currency code",
        },
        "created_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Cart creation timestamp",
        },
        "updated_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Last update timestamp",
        },
    },
    "coherence_rules": [
        "total = subtotal + tax",
        "subtotal = sum(items.quantity * items.price)",
        "items should be thematically related",
    ],
}
