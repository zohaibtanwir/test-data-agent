"""Schema registry for managing test data entity schemas."""

from typing import Dict, List, Optional

from test_data_agent.schemas.entities import (
    CART_SCHEMA,
    ORDER_SCHEMA,
    PAYMENT_SCHEMA,
    PRODUCT_SCHEMA,
    REVIEW_SCHEMA,
    USER_SCHEMA,
)
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class SchemaRegistry:
    """Registry for pre-defined entity schemas."""

    def __init__(self):
        """Initialize the schema registry."""
        self._schemas: Dict[str, dict] = {}
        self._load_predefined_schemas()
        logger.info("schema_registry_initialized", schema_count=len(self._schemas))

    def _load_predefined_schemas(self) -> None:
        """Load all pre-defined schemas."""
        schemas = [
            CART_SCHEMA,
            ORDER_SCHEMA,
            PAYMENT_SCHEMA,
            PRODUCT_SCHEMA,
            REVIEW_SCHEMA,
            USER_SCHEMA,
        ]

        for schema in schemas:
            self._validate_schema(schema)
            self._schemas[schema["name"]] = schema

        logger.info("predefined_schemas_loaded", count=len(schemas))

    def _validate_schema(self, schema: dict) -> None:
        """
        Validate a schema structure.

        Args:
            schema: Schema dictionary to validate

        Raises:
            ValueError: If schema is invalid
        """
        required_keys = ["name", "domain", "description", "fields"]
        for key in required_keys:
            if key not in schema:
                raise ValueError(f"Schema missing required key: {key}")

        if not isinstance(schema["fields"], dict):
            raise ValueError("Schema 'fields' must be a dictionary")

        if not schema["name"]:
            raise ValueError("Schema 'name' cannot be empty")

    def get_schema(self, name: str) -> Optional[dict]:
        """
        Get a schema by name.

        Args:
            name: Schema name (e.g., 'cart', 'order')

        Returns:
            Schema dictionary or None if not found
        """
        schema = self._schemas.get(name)
        if schema:
            logger.debug("schema_retrieved", name=name)
        else:
            logger.warning("schema_not_found", name=name)
        return schema

    def list_schemas(self, domain: Optional[str] = None) -> List[dict]:
        """
        List all schemas, optionally filtered by domain.

        Args:
            domain: Optional domain filter (e.g., 'ecommerce')

        Returns:
            List of schema dictionaries
        """
        schemas = list(self._schemas.values())

        if domain:
            schemas = [s for s in schemas if s.get("domain") == domain]
            logger.debug("schemas_listed_filtered", domain=domain, count=len(schemas))
        else:
            logger.debug("schemas_listed_all", count=len(schemas))

        return schemas

    def register_schema(self, schema: dict) -> None:
        """
        Register a new custom schema.

        Args:
            schema: Schema dictionary to register

        Raises:
            ValueError: If schema is invalid or name already exists
        """
        self._validate_schema(schema)

        name = schema["name"]
        if name in self._schemas:
            raise ValueError(f"Schema '{name}' already exists")

        self._schemas[name] = schema
        logger.info("schema_registered", name=name)

    def schema_exists(self, name: str) -> bool:
        """
        Check if a schema exists.

        Args:
            name: Schema name

        Returns:
            True if schema exists
        """
        return name in self._schemas

    def get_schema_info(self, name: str) -> Optional[dict]:
        """
        Get basic info about a schema (for gRPC SchemaInfo response).

        Args:
            name: Schema name

        Returns:
            Schema info dict with name, domain, description, fields
        """
        schema = self.get_schema(name)
        if not schema:
            return None

        # Convert fields dict to list of field info dictionaries
        fields_info = []
        for field_name, field_def in schema["fields"].items():
            field_info = {
                "name": field_name,
                "type": field_def.get("type", "string"),
                "required": field_def.get("required", False),
                "description": field_def.get("description", ""),
                "example": str(field_def.get("format", field_def.get("default", ""))),
            }
            fields_info.append(field_info)

        return {
            "name": schema["name"],
            "domain": schema["domain"],
            "description": schema["description"],
            "fields": fields_info,
        }


# Global registry instance
_registry: Optional[SchemaRegistry] = None


def get_registry() -> SchemaRegistry:
    """Get or create the global schema registry."""
    global _registry
    if _registry is None:
        _registry = SchemaRegistry()
    return _registry
