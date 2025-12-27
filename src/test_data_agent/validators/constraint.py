"""Constraint validator for generated test data."""

import re
from dataclasses import dataclass
from typing import Any, List, Optional

from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationError:
    """Validation error details."""

    field: str
    message: str
    value: Any


@dataclass
class ValidationResult:
    """Result of validation."""

    valid: bool
    errors: List[ValidationError]

    def __bool__(self) -> bool:
        """Allow using result in boolean context."""
        return self.valid


class ConstraintValidator:
    """Validates generated data against schema constraints."""

    def validate(
        self,
        data: dict,
        schema: dict,
        constraints: Optional[dict] = None,
    ) -> ValidationResult:
        """
        Validate data against schema and constraints.

        Args:
            data: Generated data record
            schema: Schema definition
            constraints: Optional additional constraints (from gRPC request)

        Returns:
            ValidationResult with errors if any
        """
        errors: List[ValidationError] = []

        # Get fields from schema
        schema_fields = schema.get("fields", {})

        # Validate each field
        for field_name, field_def in schema_fields.items():
            # Check required fields
            if field_def.get("required", False) and field_name not in data:
                errors.append(
                    ValidationError(
                        field=field_name,
                        message=f"Required field '{field_name}' is missing",
                        value=None,
                    )
                )
                continue

            # Skip validation if field not present and not required
            if field_name not in data:
                continue

            value = data[field_name]

            # Get constraint for this field
            field_constraint = None
            if constraints:
                field_constraint = constraints.get(field_name)

            # Validate the field
            field_errors = self.validate_field(value, field_def, field_constraint)
            errors.extend(field_errors)

        result = ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
        )

        if not result.valid:
            logger.warning("validation_failed", error_count=len(errors))

        return result

    def validate_field(
        self,
        value: Any,
        field_def: dict,
        constraint: Optional[dict] = None,
    ) -> List[ValidationError]:
        """
        Validate a single field value.

        Args:
            value: Field value to validate
            field_def: Field definition from schema
            constraint: Optional constraint definition

        Returns:
            List of validation errors
        """
        errors: List[ValidationError] = []
        field_name = field_def.get("name", "unknown")

        field_type = field_def.get("type")

        # Type-specific validation
        if field_type == "integer":
            errors.extend(self._validate_integer(value, field_def, constraint, field_name))
        elif field_type == "float":
            errors.extend(self._validate_float(value, field_def, constraint, field_name))
        elif field_type == "string":
            errors.extend(self._validate_string(value, field_def, constraint, field_name))
        elif field_type == "enum":
            errors.extend(self._validate_enum(value, field_def, constraint, field_name))
        elif field_type == "array":
            errors.extend(self._validate_array(value, field_def, constraint, field_name))
        elif field_type == "object":
            errors.extend(self._validate_object(value, field_def, constraint, field_name))

        return errors

    def _validate_integer(
        self, value: Any, field_def: dict, constraint: Optional[dict], field_name: str
    ) -> List[ValidationError]:
        """Validate integer field."""
        errors = []

        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Expected integer, got {type(value).__name__}",
                    value=value,
                )
            )
            return errors

        # Check min/max from field_def
        min_val = field_def.get("min")
        max_val = field_def.get("max")

        # Override with constraint if provided
        if constraint:
            min_val = constraint.get("min", min_val)
            max_val = constraint.get("max", max_val)

        if min_val is not None and value < min_val:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value {value} is less than minimum {min_val}",
                    value=value,
                )
            )

        if max_val is not None and value > max_val:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value {value} is greater than maximum {max_val}",
                    value=value,
                )
            )

        return errors

    def _validate_float(
        self, value: Any, field_def: dict, constraint: Optional[dict], field_name: str
    ) -> List[ValidationError]:
        """Validate float field."""
        errors = []

        if not isinstance(value, (int, float)) or isinstance(value, bool):
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Expected number, got {type(value).__name__}",
                    value=value,
                )
            )
            return errors

        # Check min/max
        min_val = field_def.get("min")
        max_val = field_def.get("max")

        if constraint:
            min_val = constraint.get("min", min_val)
            max_val = constraint.get("max", max_val)

        if min_val is not None and value < min_val:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value {value} is less than minimum {min_val}",
                    value=value,
                )
            )

        if max_val is not None and value > max_val:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value {value} is greater than maximum {max_val}",
                    value=value,
                )
            )

        return errors

    def _validate_string(
        self, value: Any, field_def: dict, constraint: Optional[dict], field_name: str
    ) -> List[ValidationError]:
        """Validate string field."""
        errors = []

        if not isinstance(value, str):
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Expected string, got {type(value).__name__}",
                    value=value,
                )
            )
            return errors

        # Check length
        min_length = field_def.get("min_length")
        max_length = field_def.get("max_length")

        if constraint:
            min_length = constraint.get("min_length", min_length)
            max_length = constraint.get("max_length", max_length)

        if min_length is not None and len(value) < min_length:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"String length {len(value)} is less than minimum {min_length}",
                    value=value,
                )
            )

        if max_length is not None and len(value) > max_length:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"String length {len(value)} is greater than maximum {max_length}",
                    value=value,
                )
            )

        # Check regex pattern
        pattern = field_def.get("pattern") or field_def.get("regex")
        if constraint:
            pattern = constraint.get("pattern") or constraint.get("regex", pattern)

        if pattern:
            if not re.match(pattern, value):
                errors.append(
                    ValidationError(
                        field=field_name,
                        message=f"String does not match pattern {pattern}",
                        value=value,
                    )
                )

        return errors

    def _validate_enum(
        self, value: Any, field_def: dict, constraint: Optional[dict], field_name: str
    ) -> List[ValidationError]:
        """Validate enum field."""
        errors = []

        # Get allowed values
        allowed = field_def.get("values", [])
        if constraint:
            allowed = constraint.get("enum_values", allowed)

        if value not in allowed:
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Value '{value}' not in allowed values: {allowed}",
                    value=value,
                )
            )

        return errors

    def _validate_array(
        self, value: Any, field_def: dict, constraint: Optional[dict], field_name: str
    ) -> List[ValidationError]:
        """Validate array field."""
        errors = []

        if not isinstance(value, list):
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Expected array, got {type(value).__name__}",
                    value=value,
                )
            )
            return errors

        # Validate array items if schema provided
        item_schema = field_def.get("item_schema")
        if item_schema:
            for idx, item in enumerate(value):
                # For object items, validate each field
                if item_schema.get("type") == "object":
                    item_fields = item_schema.get("fields", {})
                    for item_field_name, item_field_def in item_fields.items():
                        if item_field_name in item:
                            item_field_def_copy = {
                                **item_field_def,
                                "name": f"{field_name}[{idx}].{item_field_name}",
                            }
                            item_errors = self.validate_field(
                                item[item_field_name],
                                item_field_def_copy,
                                None,
                            )
                            errors.extend(item_errors)

        return errors

    def _validate_object(
        self, value: Any, field_def: dict, constraint: Optional[dict], field_name: str
    ) -> List[ValidationError]:
        """Validate object field."""
        errors = []

        if not isinstance(value, dict):
            errors.append(
                ValidationError(
                    field=field_name,
                    message=f"Expected object, got {type(value).__name__}",
                    value=value,
                )
            )
            return errors

        # Validate nested fields
        nested_fields = field_def.get("fields", {})
        for nested_field_name, nested_field_def in nested_fields.items():
            if nested_field_name in value:
                nested_field_def_copy = {
                    **nested_field_def,
                    "name": f"{field_name}.{nested_field_name}",
                }
                nested_errors = self.validate_field(
                    value[nested_field_name],
                    nested_field_def_copy,
                    None,
                )
                errors.extend(nested_errors)
            elif nested_field_def.get("required", False):
                errors.append(
                    ValidationError(
                        field=f"{field_name}.{nested_field_name}",
                        message=f"Required nested field '{nested_field_name}' is missing",
                        value=None,
                    )
                )

        return errors
