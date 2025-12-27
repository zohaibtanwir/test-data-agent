"""Traditional generator using Faker for data generation."""

import random
import time
from datetime import datetime
from typing import Any, AsyncIterator

from faker import Faker

from test_data_agent.generators.base import BaseGenerator, GenerationResult
from test_data_agent.proto import test_data_pb2
from test_data_agent.schemas.registry import get_registry
from test_data_agent.utils.logging import get_logger
from test_data_agent.validators.constraint import ConstraintValidator

logger = get_logger(__name__)


class TraditionalGenerator(BaseGenerator):
    """Faker-based data generator for simple, fast generation."""

    def __init__(self):
        """Initialize the traditional generator."""
        self.faker = Faker()
        self.registry = get_registry()
        self.validator = ConstraintValidator()
        logger.info("traditional_generator_initialized")

    async def generate(
        self,
        request: test_data_pb2.GenerateRequest,
        context: dict | None = None,
    ) -> GenerationResult:
        """
        Generate test data using Faker.

        Args:
            request: Generate data request
            context: Optional context (unused for traditional)

        Returns:
            GenerationResult with generated data
        """
        start_time = time.time()

        # Get schema
        schema = self._get_schema(request)

        # Distribute count across scenarios
        scenario_distribution = self._calculate_scenario_distribution(request)

        # Generate records
        all_records = []
        for scenario_name, scenario_count in scenario_distribution.items():
            scenario_overrides = self._get_scenario_overrides(request, scenario_name)

            for _ in range(scenario_count):
                record = self._generate_record(schema, scenario_overrides)
                record["_scenario"] = scenario_name
                all_records.append(record)

        # Add index metadata
        all_records = self._add_metadata_fields(all_records)

        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "traditional_generation_complete",
            request_id=request.request_id,
            count=len(all_records),
            duration_ms=duration_ms,
        )

        return GenerationResult(
            data=all_records,
            metadata={
                "generation_path": "traditional",
                "duration_ms": duration_ms,
                "record_count": len(all_records),
            },
        )

    async def generate_stream(
        self,
        request: test_data_pb2.GenerateRequest,
        batch_size: int = 50,
        context: dict | None = None,
    ) -> AsyncIterator[GenerationResult]:
        """
        Stream records in batches.

        Args:
            request: Generate data request
            batch_size: Records per batch
            context: Optional context

        Yields:
            GenerationResult for each batch
        """
        # Use default implementation from base
        async for batch in super().generate_stream(request, batch_size, context):
            yield batch

    def supports(self, request: test_data_pb2.GenerateRequest) -> bool:
        """
        Check if traditional generator supports this request.

        Args:
            request: Generate data request

        Returns:
            True - traditional generator supports all requests as fallback
        """
        # Traditional generator can handle any request, but is best for:
        # - Simple data types
        # - High volume
        # - No coherence requirements
        return True

    def _get_schema(self, request: test_data_pb2.GenerateRequest) -> dict:
        """Get schema from request or registry."""
        # Check if predefined schema is requested
        if request.schema and request.schema.predefined_schema:
            schema = self.registry.get_schema(request.schema.predefined_schema)
            if schema:
                return schema

        # Use schema from request (would need conversion from proto)
        # For now, default to entity-based lookup
        if request.entity:
            schema = self.registry.get_schema(request.entity)
            if schema:
                return schema

        # Fallback: minimal schema
        return {
            "name": "generic",
            "domain": request.domain or "unknown",
            "fields": {},
        }

    def _calculate_scenario_distribution(
        self, request: test_data_pb2.GenerateRequest
    ) -> dict[str, int]:
        """Calculate how many records per scenario."""
        if not request.scenarios:
            return {"default": request.count}

        distribution = {}
        for scenario in request.scenarios:
            distribution[scenario.name] = scenario.count

        # Verify total matches request count
        total = sum(distribution.values())
        if total != request.count:
            logger.warning(
                "scenario_count_mismatch",
                expected=request.count,
                actual=total,
            )

        return distribution

    def _get_scenario_overrides(
        self, request: test_data_pb2.GenerateRequest, scenario_name: str
    ) -> dict:
        """Get field overrides for a scenario."""
        for scenario in request.scenarios:
            if scenario.name == scenario_name:
                return dict(scenario.overrides)
        return {}

    def _generate_record(self, schema: dict, overrides: dict) -> dict:
        """Generate a single record."""
        record = {}
        fields = schema.get("fields", {})

        for field_name, field_def in fields.items():
            # Use override if provided
            if field_name in overrides:
                record[field_name] = overrides[field_name]
                continue

            # Generate value based on field type
            record[field_name] = self._generate_field_value(field_name, field_def)

        return record

    def _generate_field_value(self, field_name: str, field_def: dict) -> Any:
        """Generate value for a field."""
        field_type = field_def.get("type", "string")

        # Handle different field types
        if field_type == "string":
            return self._generate_string(field_name, field_def)
        elif field_type == "integer":
            return self._generate_integer(field_def)
        elif field_type == "float":
            return self._generate_float(field_def)
        elif field_type == "boolean":
            return self.faker.boolean()
        elif field_type == "date":
            return self._generate_date(field_def)
        elif field_type == "datetime":
            return self._generate_datetime(field_def)
        elif field_type == "email":
            return self.faker.email()
        elif field_type == "phone":
            return self.faker.phone_number()
        elif field_type == "address":
            return self.faker.address()
        elif field_type == "uuid":
            return str(self.faker.uuid4())
        elif field_type == "enum":
            return self._generate_enum(field_def)
        elif field_type == "object":
            return self._generate_object(field_def)
        elif field_type == "array":
            return self._generate_array(field_def)
        else:
            return self.faker.word()

    def _generate_string(self, field_name: str, field_def: dict) -> str:
        """Generate string value."""
        # Check for custom format
        format_str = field_def.get("format")
        if format_str:
            return self._apply_format(format_str)

        # Use faker based on field name hints
        field_lower = field_name.lower()

        if "name" in field_lower:
            if "first" in field_lower:
                return self.faker.first_name()
            elif "last" in field_lower:
                return self.faker.last_name()
            else:
                return self.faker.name()
        elif "email" in field_lower:
            return self.faker.email()
        elif "phone" in field_lower:
            return self.faker.phone_number()
        elif "address" in field_lower or "street" in field_lower:
            return self.faker.street_address()
        elif "city" in field_lower:
            return self.faker.city()
        elif "state" in field_lower:
            return self.faker.state_abbr()
        elif "zip" in field_lower:
            return self.faker.zipcode()
        elif "country" in field_lower:
            return field_def.get("default", "US")
        elif "title" in field_lower:
            return self.faker.sentence(nb_words=6)[:-1]  # Remove period
        elif "body" in field_lower or "description" in field_lower:
            return self.faker.paragraph(nb_sentences=3)
        elif "sku" in field_lower:
            category = random.choice(["APP", "HOME", "BEAUTY", "JEWELRY"])
            return f"{category}-{self.faker.numerify('######')}"
        else:
            # Respect min/max length if provided
            min_length = field_def.get("min_length", 5)
            max_length = field_def.get("max_length", 20)
            return self.faker.pystr(min_chars=min_length, max_chars=max_length)

    def _generate_integer(self, field_def: dict) -> int:
        """Generate integer value."""
        min_val = int(field_def.get("min", 0))
        max_val = int(field_def.get("max", 100))
        return random.randint(min_val, max_val)

    def _generate_float(self, field_def: dict) -> float:
        """Generate float value."""
        min_val = float(field_def.get("min", 0.0))
        max_val = float(field_def.get("max", 1000.0))
        value = random.uniform(min_val, max_val)
        return round(value, 2)

    def _generate_date(self, field_def: dict) -> str:
        """Generate date value."""
        date = self.faker.date_this_year()
        return date.isoformat()

    def _generate_datetime(self, field_def: dict) -> str:
        """Generate datetime value."""
        dt = self.faker.date_time_this_year()
        return dt.isoformat()

    def _generate_enum(self, field_def: dict) -> str:
        """Generate enum value."""
        values = field_def.get("values", [])
        if not values:
            return ""

        default = field_def.get("default")
        if default:
            # Use default 50% of the time
            if random.random() < 0.5:
                return default

        return random.choice(values)

    def _generate_object(self, field_def: dict) -> dict:
        """Generate nested object."""
        obj = {}
        nested_fields = field_def.get("fields", {})

        for nested_name, nested_def in nested_fields.items():
            obj[nested_name] = self._generate_field_value(nested_name, nested_def)

        return obj

    def _generate_array(self, field_def: dict) -> list:
        """Generate array of items."""
        # Random array length (2-5 items)
        length = random.randint(2, 5)

        items = []
        item_schema = field_def.get("item_schema", {})

        for _ in range(length):
            if item_schema.get("type") == "object":
                item = self._generate_object(item_schema)
            else:
                item = self._generate_field_value("item", item_schema)
            items.append(item)

        return items

    def _apply_format(self, format_str: str) -> str:
        """Apply custom format string."""
        # Replace placeholders: {year}, {random:N}
        result = format_str

        # Year
        if "{year}" in result:
            result = result.replace("{year}", str(datetime.now().year))

        # Random digits
        import re

        pattern = r"\{random:(\d+)\}"
        matches = re.findall(pattern, result)
        for match in matches:
            length = int(match)
            random_digits = "".join([str(random.randint(0, 9)) for _ in range(length)])
            result = result.replace(f"{{random:{match}}}", random_digits, 1)

        return result
