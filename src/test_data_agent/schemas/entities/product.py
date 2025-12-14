"""Product schema definition."""

PRODUCT_SCHEMA = {
    "name": "product",
    "domain": "ecommerce",
    "description": "Product catalog item",
    "fields": {
        "product_id": {
            "type": "string",
            "required": True,
            "faker": "uuid4",
        },
        "name": {
            "type": "string",
            "required": True,
            "faker": "catch_phrase",
        },
        "description": {
            "type": "string",
            "required": False,
            "faker": "text",
            "max_nb_chars": 200,
        },
        "price": {
            "type": "float",
            "required": True,
            "faker": "pyfloat",
            "min_value": 5.0,
            "max_value": 999.99,
            "right_digits": 2,
        },
        "category": {
            "type": "string",
            "required": True,
            "faker": "random_element",
            "elements": ["Electronics", "Clothing", "Home", "Beauty", "Sports"],
        },
        "sku": {
            "type": "string",
            "required": True,
            "pattern": "{category}-{random_int:6}",
        },
        "in_stock": {
            "type": "boolean",
            "required": True,
            "faker": "boolean",
            "chance_of_getting_true": 85,
        },
        "stock_quantity": {
            "type": "integer",
            "required": True,
            "faker": "random_int",
            "min": 0,
            "max": 500,
        },
        "brand": {
            "type": "string",
            "required": True,
            "faker": "company",
        },
        "created_at": {
            "type": "datetime",
            "required": True,
            "faker": "date_time_this_year",
        },
        "updated_at": {
            "type": "datetime",
            "required": True,
            "faker": "date_time_this_month",
        },
    },
}
