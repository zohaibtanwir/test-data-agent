"""Cart item schema definition."""

CART_ITEM_SCHEMA = {
    "name": "cart_item",
    "domain": "ecommerce",
    "description": "Individual item in a shopping cart",
    "fields": {
        "cart_item_id": {
            "type": "string",
            "format": "CI-{year}-{random:7}",
            "required": True,
            "description": "Unique cart item identifier",
        },
        "cart_id": {
            "type": "string",
            "format": "CRT-{year}-{random:7}",
            "required": True,
            "description": "Parent cart ID",
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
            "max": 99,
            "required": True,
            "description": "Item quantity",
        },
        "unit_price": {
            "type": "float",
            "min": 0.01,
            "required": True,
            "description": "Price per unit",
        },
        "total_price": {
            "type": "float",
            "min": 0.01,
            "required": True,
            "description": "Line item total",
        },
        "added_at": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "When item was added to cart",
        },
    },
    "coherence_rules": [
        "total_price = quantity * unit_price",
        "quantity must be between 1 and 99",
    ],
}
