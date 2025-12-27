"""Unit tests for schema registry."""

import pytest

from test_data_agent.schemas.registry import SchemaRegistry


def test_get_schema():
    """Test getting a schema by name."""
    registry = SchemaRegistry()

    cart_schema = registry.get_schema("cart")
    assert cart_schema is not None
    assert cart_schema["name"] == "cart"
    assert cart_schema["domain"] == "ecommerce"
    assert "cart_id" in cart_schema["fields"]


def test_list_schemas():
    """Test listing all schemas."""
    registry = SchemaRegistry()

    schemas = registry.list_schemas()
    assert len(schemas) == 36  # All 36 ecommerce entity schemas

    names = {s["name"] for s in schemas}
    expected_names = {
        "analytics_event", "cart", "cart_item", "coupon", "customer",
        "customer_preferences", "discount", "exchange", "favorites",
        "fraud_check", "gift_card", "inventory", "loyalty_member",
        "notification", "order", "order_item", "order_status", "payment",
        "payment_authorization", "product", "promotion", "rating", "refund",
        "return", "review", "saved_cart", "search_query", "shipment",
        "shipping", "stock", "stock_alert", "subscription", "support_ticket",
        "tracking", "user", "wishlist",
    }
    assert names == expected_names


def test_list_schemas_filtered():
    """Test listing schemas filtered by domain."""
    registry = SchemaRegistry()

    ecommerce_schemas = registry.list_schemas(domain="ecommerce")
    assert len(ecommerce_schemas) == 36  # All current schemas are ecommerce

    # Test non-existent domain
    other_schemas = registry.list_schemas(domain="supply_chain")
    assert len(other_schemas) == 0


def test_invalid_schema():
    """Test that invalid schema raises error."""
    registry = SchemaRegistry()

    invalid_schema = {"name": "invalid"}  # Missing required fields

    with pytest.raises(ValueError) as exc_info:
        registry.register_schema(invalid_schema)

    assert "missing required key" in str(exc_info.value).lower()


def test_schema_exists():
    """Test checking if schema exists."""
    registry = SchemaRegistry()

    assert registry.schema_exists("cart") is True
    assert registry.schema_exists("order") is True
    assert registry.schema_exists("nonexistent") is False


def test_get_schema_info():
    """Test getting schema info with full field details."""
    registry = SchemaRegistry()

    info = registry.get_schema_info("cart")
    assert info is not None
    assert info["name"] == "cart"
    assert info["domain"] == "ecommerce"
    assert isinstance(info["fields"], list)

    # Fields are now dictionaries with name, type, required, description, example
    field_names = [f["name"] for f in info["fields"]]
    assert "cart_id" in field_names
    assert "customer_id" in field_names
    assert "items" in field_names

    # Verify field structure
    cart_id_field = next(f for f in info["fields"] if f["name"] == "cart_id")
    assert cart_id_field["type"] == "string"
    assert cart_id_field["required"] is True
    assert "description" in cart_id_field
    assert "example" in cart_id_field


def test_register_custom_schema():
    """Test registering a custom schema."""
    registry = SchemaRegistry()

    custom_schema = {
        "name": "custom_entity",
        "domain": "test",
        "description": "Custom test entity",
        "fields": {
            "id": {"type": "string", "required": True},
            "name": {"type": "string", "required": True},
        },
    }

    registry.register_schema(custom_schema)

    # Verify it was registered
    assert registry.schema_exists("custom_entity")
    retrieved = registry.get_schema("custom_entity")
    assert retrieved["name"] == "custom_entity"


def test_register_duplicate_schema():
    """Test that registering duplicate schema raises error."""
    registry = SchemaRegistry()

    # Try to register 'cart' again
    cart_schema = registry.get_schema("cart")

    with pytest.raises(ValueError) as exc_info:
        registry.register_schema(cart_schema)

    assert "already exists" in str(exc_info.value).lower()
