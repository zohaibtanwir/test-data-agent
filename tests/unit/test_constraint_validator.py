"""Unit tests for constraint validator."""

import pytest

from test_data_agent.validators.constraint import ConstraintValidator


@pytest.fixture
def validator():
    """Fixture for constraint validator."""
    return ConstraintValidator()


def test_validate_min_max_integer(validator):
    """Test integer min/max validation."""
    field_def = {"type": "integer", "min": 1, "max": 10, "name": "quantity"}

    # Valid value
    errors = validator.validate_field(5, field_def, None)
    assert len(errors) == 0

    # Below min
    errors = validator.validate_field(0, field_def, None)
    assert len(errors) == 1
    assert "less than minimum" in errors[0].message

    # Above max
    errors = validator.validate_field(11, field_def, None)
    assert len(errors) == 1
    assert "greater than maximum" in errors[0].message


def test_validate_min_max_float(validator):
    """Test float min/max validation."""
    field_def = {"type": "float", "min": 0.01, "max": 100.0, "name": "price"}

    # Valid value
    errors = validator.validate_field(50.0, field_def, None)
    assert len(errors) == 0

    # Below min
    errors = validator.validate_field(0.001, field_def, None)
    assert len(errors) == 1

    # Above max
    errors = validator.validate_field(100.1, field_def, None)
    assert len(errors) == 1


def test_validate_string_length(validator):
    """Test string length validation."""
    field_def = {"type": "string", "min_length": 5, "max_length": 20, "name": "name"}

    # Valid value
    errors = validator.validate_field("test name", field_def, None)
    assert len(errors) == 0

    # Too short
    errors = validator.validate_field("abc", field_def, None)
    assert len(errors) == 1
    assert "less than minimum" in errors[0].message

    # Too long
    errors = validator.validate_field("a" * 25, field_def, None)
    assert len(errors) == 1
    assert "greater than maximum" in errors[0].message


def test_validate_enum(validator):
    """Test enum validation."""
    field_def = {"type": "enum", "values": ["red", "green", "blue"], "name": "color"}

    # Valid value
    errors = validator.validate_field("red", field_def, None)
    assert len(errors) == 0

    # Invalid value
    errors = validator.validate_field("yellow", field_def, None)
    assert len(errors) == 1
    assert "not in allowed values" in errors[0].message


def test_validate_regex(validator):
    """Test regex pattern validation."""
    field_def = {"type": "string", "pattern": r"^\d{4}$", "name": "code"}

    # Valid value
    errors = validator.validate_field("1234", field_def, None)
    assert len(errors) == 0

    # Invalid value
    errors = validator.validate_field("12345", field_def, None)
    assert len(errors) == 1
    assert "does not match pattern" in errors[0].message


def test_validate_nested_object(validator):
    """Test nested object validation."""
    field_def = {
        "type": "object",
        "name": "address",
        "fields": {
            "street": {"type": "string", "required": True, "name": "street"},
            "city": {"type": "string", "required": True, "name": "city"},
            "zip": {"type": "string", "pattern": r"^\d{5}$", "name": "zip"},
        },
    }

    # Valid object
    valid_data = {"street": "123 Main St", "city": "Boston", "zip": "02101"}
    errors = validator.validate_field(valid_data, field_def, None)
    assert len(errors) == 0

    # Missing required field
    invalid_data = {"street": "123 Main St"}
    errors = validator.validate_field(invalid_data, field_def, None)
    assert len(errors) == 1
    assert "Required nested field" in errors[0].message


def test_validate_array(validator):
    """Test array validation."""
    field_def = {
        "type": "array",
        "name": "items",
        "item_schema": {
            "type": "object",
            "fields": {
                "quantity": {"type": "integer", "min": 1, "max": 10, "name": "quantity"},
                "price": {"type": "float", "min": 0.01, "name": "price"},
            },
        },
    }

    # Valid array
    valid_data = [
        {"quantity": 2, "price": 10.99},
        {"quantity": 5, "price": 5.99},
    ]
    errors = validator.validate_field(valid_data, field_def, None)
    assert len(errors) == 0

    # Invalid item (quantity out of range)
    invalid_data = [{"quantity": 15, "price": 10.99}]
    errors = validator.validate_field(invalid_data, field_def, None)
    assert len(errors) > 0


def test_returns_all_errors(validator):
    """Test that validator returns all errors, not just the first."""
    schema = {
        "fields": {
            "quantity": {"type": "integer", "min": 1, "max": 10, "required": True},
            "price": {"type": "float", "min": 0.01, "required": True},
            "status": {"type": "enum", "values": ["active", "inactive"], "required": True},
        }
    }

    # Data with multiple errors
    data = {
        "quantity": 15,  # Above max
        "price": 0.001,  # Below min
        "status": "pending",  # Not in enum
    }

    result = validator.validate(data, schema)
    assert not result.valid
    assert len(result.errors) == 3  # Should have all 3 errors


def test_required_field_missing(validator):
    """Test that missing required field is caught."""
    schema = {
        "fields": {
            "name": {"type": "string", "required": True},
            "optional": {"type": "string", "required": False},
        }
    }

    # Missing required field
    data = {"optional": "value"}
    result = validator.validate(data, schema)

    assert not result.valid
    assert len(result.errors) == 1
    assert "Required field" in result.errors[0].message


def test_constraint_override(validator):
    """Test that constraint parameter overrides field definition."""
    field_def = {"type": "integer", "min": 1, "max": 10, "name": "value"}

    # Override with stricter constraint
    constraint = {"min": 5, "max": 8}

    # Value valid in field_def but invalid in constraint
    errors = validator.validate_field(3, field_def, constraint)
    assert len(errors) == 1
    assert "less than minimum 5" in errors[0].message
