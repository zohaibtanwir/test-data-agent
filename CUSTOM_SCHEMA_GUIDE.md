# Custom Schema Generation Guide

## Overview

You can generate test data for custom schemas in **3 ways**:

1. **Method 1:** Add schema to codebase (permanent)
2. **Method 2:** Pass inline schema via gRPC (dynamic)
3. **Method 3:** Use Python API directly (programmatic)

---

## Method 1: Add Schema to Codebase (Recommended)

This is the best approach for schemas you'll use repeatedly.

### Step 1: Create Schema File

Create a new file in `src/test_data_agent/schemas/entities/`:

```python
# src/test_data_agent/schemas/entities/employee.py

"""Employee schema definition."""

EMPLOYEE_SCHEMA = {
    "name": "employee",
    "domain": "hr",
    "description": "Employee record",
    "fields": {
        "employee_id": {
            "type": "string",
            "format": "EMP-{year}-{random:5}",
            "required": True,
            "description": "Unique employee identifier",
        },
        "first_name": {
            "type": "string",
            "required": True,
            "description": "First name",
        },
        "last_name": {
            "type": "string",
            "required": True,
            "description": "Last name",
        },
        "email": {
            "type": "string",
            "format": "email",
            "required": True,
            "description": "Work email",
        },
        "department": {
            "type": "enum",
            "values": ["Engineering", "Sales", "Marketing", "HR", "Finance"],
            "required": True,
            "description": "Department",
        },
        "salary": {
            "type": "float",
            "min": 30000.0,
            "max": 250000.0,
            "required": True,
            "description": "Annual salary in USD",
        },
        "hire_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Hire date",
        },
        "is_active": {
            "type": "boolean",
            "default": True,
            "required": False,
            "description": "Employment status",
        },
        "manager_id": {
            "type": "string",
            "required": False,
            "description": "Manager's employee ID",
        },
    },
}
```

### Step 2: Register in Schema Registry

Edit `src/test_data_agent/schemas/entities/__init__.py`:

```python
from .cart import CART_SCHEMA
from .order import ORDER_SCHEMA
from .payment import PAYMENT_SCHEMA
from .product import PRODUCT_SCHEMA
from .review import REVIEW_SCHEMA
from .user import USER_SCHEMA
from .employee import EMPLOYEE_SCHEMA  # Add this

__all__ = [
    "CART_SCHEMA",
    "ORDER_SCHEMA",
    "PAYMENT_SCHEMA",
    "PRODUCT_SCHEMA",
    "REVIEW_SCHEMA",
    "USER_SCHEMA",
    "EMPLOYEE_SCHEMA",  # Add this
]
```

### Step 3: Load in Registry

Edit `src/test_data_agent/schemas/registry.py`:

```python
from test_data_agent.schemas.entities import (
    CART_SCHEMA,
    ORDER_SCHEMA,
    PAYMENT_SCHEMA,
    PRODUCT_SCHEMA,
    REVIEW_SCHEMA,
    USER_SCHEMA,
    EMPLOYEE_SCHEMA,  # Add this
)

# In _load_predefined_schemas method:
def _load_predefined_schemas(self) -> None:
    """Load all pre-defined schemas."""
    schemas = [
        CART_SCHEMA,
        ORDER_SCHEMA,
        PAYMENT_SCHEMA,
        PRODUCT_SCHEMA,
        REVIEW_SCHEMA,
        USER_SCHEMA,
        EMPLOYEE_SCHEMA,  # Add this
    ]
    # ... rest of method
```

### Step 4: Restart Service & Test

```bash
# Restart service
pkill -f "python -m test_data_agent.main"
python -m test_data_agent.main &

# Wait for startup
sleep 3

# Test generation
grpcurl -plaintext -d '{
  "request_id": "test-employee-1",
  "domain": "hr",
  "entity": "employee",
  "count": 10
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

---

## Method 2: Inline Schema via gRPC (Dynamic)

For one-off schemas or testing, pass the schema inline:

```bash
grpcurl -plaintext -d '{
  "request_id": "inline-test-1",
  "entity": "custom_entity",
  "count": 5,
  "inline_schema": {
    "name": "custom_entity",
    "domain": "custom",
    "description": "Custom entity for testing",
    "fields": {
      "id": {
        "type": "string",
        "required": true,
        "description": "Unique ID"
      },
      "name": {
        "type": "string",
        "required": true,
        "description": "Entity name"
      },
      "value": {
        "type": "integer",
        "min": 0,
        "max": 1000,
        "required": true,
        "description": "Numeric value"
      },
      "created_at": {
        "type": "datetime",
        "format": "iso8601",
        "required": true,
        "description": "Creation timestamp"
      }
    }
  }
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Note:** Check if `inline_schema` field exists in the proto definition. If not, use Method 1 or 3.

---

## Method 3: Python API (Programmatic)

Use the Python API directly:

```python
#!/usr/bin/env python3
"""Generate data for custom schema using Python API."""

import asyncio
import json
from test_data_agent.schemas.registry import SchemaRegistry
from test_data_agent.generators.traditional import TraditionalGenerator
from test_data_agent.validators.constraint import ConstraintValidator
from test_data_agent.proto import test_data_pb2

# Define custom schema
CUSTOM_SCHEMA = {
    "name": "book",
    "domain": "library",
    "description": "Book record",
    "fields": {
        "isbn": {
            "type": "string",
            "required": True,
            "description": "ISBN number",
        },
        "title": {
            "type": "string",
            "required": True,
            "description": "Book title",
        },
        "author": {
            "type": "string",
            "required": True,
            "description": "Author name",
        },
        "pages": {
            "type": "integer",
            "min": 10,
            "max": 2000,
            "required": True,
            "description": "Number of pages",
        },
        "price": {
            "type": "float",
            "min": 5.99,
            "max": 199.99,
            "required": True,
            "description": "Price in USD",
        },
        "genre": {
            "type": "enum",
            "values": ["Fiction", "Non-Fiction", "Science", "History", "Biography"],
            "required": True,
            "description": "Book genre",
        },
        "published_date": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
            "description": "Publication date",
        },
    },
}

async def generate_custom_data():
    """Generate data for custom schema."""
    # Initialize components
    schema_registry = SchemaRegistry()
    constraint_validator = ConstraintValidator()
    generator = TraditionalGenerator(schema_registry, constraint_validator)

    # Register custom schema
    schema_registry.register_schema(CUSTOM_SCHEMA)

    # Create request
    request = test_data_pb2.GenerateRequest(
        request_id="custom-python-1",
        domain="library",
        entity="book",
        count=10,
    )

    # Generate data
    result = await generator.generate(request)

    # Print results
    print(f"Generated {len(result.data)} records:")
    print(json.dumps(result.data, indent=2))

if __name__ == "__main__":
    asyncio.run(generate_custom_data())
```

**Run it:**
```bash
python my_custom_generator.py
```

---

## Schema Field Types & Formats

### Supported Field Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text field | "John Doe" |
| `integer` | Whole number | 42 |
| `float` | Decimal number | 19.99 |
| `boolean` | True/False | true |
| `datetime` | Timestamp | "2025-12-13T10:30:00Z" |
| `enum` | Fixed values | "Active" from ["Active", "Inactive"] |
| `array` | List of items | [{"sku": "ABC", "qty": 2}] |
| `object` | Nested structure | {"street": "123 Main", "city": "NYC"} |

### Field Attributes

```python
{
    "type": "string",           # Required: data type
    "required": True,           # Optional: is field mandatory?
    "default": "N/A",          # Optional: default value
    "description": "...",       # Optional: field description

    # String-specific
    "format": "email",         # email, phone, url, uuid, iso8601
    "min_length": 5,           # Minimum length
    "max_length": 100,         # Maximum length
    "regex": "^[A-Z]{3}$",    # Regex pattern

    # Number-specific (integer/float)
    "min": 0,                  # Minimum value
    "max": 1000,               # Maximum value

    # Enum-specific
    "values": ["A", "B"],      # Allowed values

    # Array-specific
    "item_schema": {...},      # Schema for array items
    "min_items": 1,            # Minimum array length
    "max_items": 10,           # Maximum array length
}
```

---

## Example Custom Schemas

### 1. IoT Sensor Data

```python
SENSOR_SCHEMA = {
    "name": "sensor",
    "domain": "iot",
    "description": "IoT sensor reading",
    "fields": {
        "sensor_id": {
            "type": "string",
            "format": "SNS-{random:8}",
            "required": True,
        },
        "device_type": {
            "type": "enum",
            "values": ["temperature", "humidity", "pressure", "motion"],
            "required": True,
        },
        "value": {
            "type": "float",
            "min": -50.0,
            "max": 150.0,
            "required": True,
        },
        "unit": {
            "type": "string",
            "required": True,
        },
        "location": {
            "type": "object",
            "fields": {
                "latitude": {"type": "float", "min": -90, "max": 90},
                "longitude": {"type": "float", "min": -180, "max": 180},
            },
            "required": True,
        },
        "timestamp": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
        },
        "battery_level": {
            "type": "integer",
            "min": 0,
            "max": 100,
            "required": False,
        },
    },
}
```

### 2. Banking Transaction

```python
TRANSACTION_SCHEMA = {
    "name": "transaction",
    "domain": "banking",
    "description": "Financial transaction",
    "fields": {
        "transaction_id": {
            "type": "string",
            "format": "TXN-{year}{month}{day}-{random:10}",
            "required": True,
        },
        "account_number": {
            "type": "string",
            "regex": "^\\d{10,12}$",
            "required": True,
        },
        "transaction_type": {
            "type": "enum",
            "values": ["deposit", "withdrawal", "transfer", "payment"],
            "required": True,
        },
        "amount": {
            "type": "float",
            "min": 0.01,
            "max": 1000000.00,
            "required": True,
        },
        "currency": {
            "type": "enum",
            "values": ["USD", "EUR", "GBP", "CAD"],
            "default": "USD",
            "required": True,
        },
        "status": {
            "type": "enum",
            "values": ["pending", "completed", "failed", "cancelled"],
            "default": "pending",
            "required": True,
        },
        "merchant": {
            "type": "string",
            "required": False,
        },
        "timestamp": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
        },
    },
}
```

### 3. Healthcare Patient

```python
PATIENT_SCHEMA = {
    "name": "patient",
    "domain": "healthcare",
    "description": "Patient medical record",
    "fields": {
        "patient_id": {
            "type": "string",
            "format": "PAT-{random:8}",
            "required": True,
        },
        "mrn": {
            "type": "string",
            "description": "Medical Record Number",
            "regex": "^MRN\\d{8}$",
            "required": True,
        },
        "full_name": {
            "type": "string",
            "required": True,
        },
        "date_of_birth": {
            "type": "datetime",
            "format": "iso8601",
            "required": True,
        },
        "gender": {
            "type": "enum",
            "values": ["Male", "Female", "Other", "Prefer not to say"],
            "required": True,
        },
        "blood_type": {
            "type": "enum",
            "values": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
            "required": False,
        },
        "allergies": {
            "type": "array",
            "item_schema": {
                "type": "string",
            },
            "required": False,
        },
        "emergency_contact": {
            "type": "object",
            "fields": {
                "name": {"type": "string", "required": True},
                "relationship": {"type": "string", "required": True},
                "phone": {"type": "string", "format": "phone", "required": True},
            },
            "required": True,
        },
    },
}
```

---

## Testing Custom Schemas

### 1. Verify Schema Loaded

```bash
grpcurl -plaintext -d '{}' localhost:9091 testdata.v1.TestDataService/GetSchemas | jq '.schemas[] | select(.name=="employee")'
```

### 2. Generate Data

```bash
grpcurl -plaintext -d '{
  "entity": "employee",
  "count": 10
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

### 3. Test with LLM

```bash
grpcurl -plaintext -d '{
  "entity": "employee",
  "count": 5,
  "context": "Generate employee records for a tech startup",
  "hints": ["realistic"]
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

### 4. Test with Constraints

```bash
grpcurl -plaintext -d '{
  "entity": "employee",
  "count": 10,
  "constraints": {
    "field_constraints": {
      "department": {
        "enum_values": ["Engineering"]
      },
      "salary": {
        "min": 80000.0,
        "max": 150000.0
      }
    }
  }
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

---

## Best Practices

### 1. Schema Design

✅ **DO:**
- Use descriptive field names
- Add field descriptions
- Set appropriate min/max constraints
- Use enums for fixed values
- Include required timestamps

❌ **DON'T:**
- Use overly generic field names
- Skip validation constraints
- Forget to mark required fields
- Use vague descriptions

### 2. Field Naming

```python
# Good
"employee_id"      # Clear, specific
"annual_salary"    # Units specified
"is_active"        # Boolean intent clear

# Bad
"id"              # Too generic
"amount"          # Ambiguous
"flag"            # Unclear meaning
```

### 3. Constraints

```python
# Good - realistic constraints
"age": {"type": "integer", "min": 18, "max": 75}
"email": {"type": "string", "format": "email"}
"phone": {"type": "string", "regex": "^\\+1\\d{10}$"}

# Bad - too permissive
"age": {"type": "integer"}  # No bounds
"email": {"type": "string"}  # No validation
```

### 4. Testing

Always test with:
1. Minimum count (1 record)
2. Medium count (10-50 records)
3. Large count (100+ records)
4. With constraints
5. With LLM path (if text fields)

---

## Troubleshooting

### Schema Not Found

```bash
# Error: "schema_not_found"

# Solution: Check schema is registered
grpcurl -plaintext -d '{}' localhost:9091 testdata.v1.TestDataService/GetSchemas | jq '.schemas[].name'
```

### Validation Errors

```bash
# Error: "constraint_violation"

# Solution: Check field constraints match data types
# Example: min/max only work with integer/float
```

### Generation Fails

```bash
# Error: "generation_failed"

# Solution: Check logs
tail -50 /tmp/test_data_agent.log | grep error
```

---

## Quick Start Checklist

- [ ] Create schema file in `entities/`
- [ ] Import in `entities/__init__.py`
- [ ] Add to registry in `registry.py`
- [ ] Restart service
- [ ] Verify with `GetSchemas`
- [ ] Test generation with small count
- [ ] Test with constraints
- [ ] Test with LLM if text fields
- [ ] Document your schema

---

**Next Steps:**
1. Create your custom schema
2. Add it following Method 1
3. Restart the service
4. Test with the commands above

Need help? Check the existing schemas in `src/test_data_agent/schemas/entities/` for more examples!
