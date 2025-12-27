"""Inventory schema definition."""

INVENTORY_SCHEMA = {
    "name": "inventory",
    "domain": "ecommerce",
    "description": "Product inventory tracking stock levels and availability",
    "fields": {
        "inventory_id": {
            "type": "string",
            "format": "INV-{year}-{random:7}",
            "required": True,
            "description": "Unique inventory record identifier",
        },
        "product_id": {
            "type": "string",
            "format": "PRD-{random:7}",
            "required": True,
            "description": "Associated product identifier",
        },
        "sku": {
            "type": "string",
            "required": True,
            "description": "Stock keeping unit",
        },
        "location_id": {
            "type": "string",
            "required": True,
            "description": "Warehouse or store location",
        },
        "quantity_on_hand": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Current stock quantity",
        },
        "quantity_reserved": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Reserved for pending orders",
        },
        "quantity_available": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Available for sale",
        },
        "reorder_point": {
            "type": "integer",
            "min": 0,
            "required": True,
            "description": "Minimum stock before reorder",
        },
        "reorder_quantity": {
            "type": "integer",
            "min": 1,
            "required": True,
            "description": "Quantity to reorder",
        },
        "unit_cost": {
            "type": "float",
            "min": 0,
            "required": True,
            "description": "Cost per unit",
        },
        "last_restock_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": False,
            "description": "Last restocking date",
        },
        "status": {
            "type": "enum",
            "values": ["in_stock", "low_stock", "out_of_stock", "discontinued"],
            "default": "in_stock",
            "required": True,
            "description": "Inventory status",
        },
    },
    "coherence_rules": [
        "quantity_available = quantity_on_hand - quantity_reserved",
        "Alert when quantity_available < reorder_point",
    ],
}
