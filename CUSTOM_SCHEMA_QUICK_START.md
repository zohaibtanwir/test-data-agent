# Custom Schema - Quick Start

## ✅ Working Example

I've created a complete working example at `/tmp/example_custom_schema.py`

**Run it:**
```bash
python /tmp/example_custom_schema.py
```

**Output:** Generates 5 employee records and saves to `/tmp/employees.json`

---

## 📋 3 Methods to Generate Custom Schema Data

### Method 1: Python API (Easiest for Testing)

```python
from test_data_agent.schemas.registry import get_registry
from test_data_agent.generators.traditional import TraditionalGenerator
from test_data_agent.proto import test_data_pb2

# Your custom schema
MY_SCHEMA = {
    "name": "my_entity",
    "domain": "my_domain",
    "description": "Description",
    "fields": {
        "id": {"type": "string", "required": True},
        "name": {"type": "string", "required": True},
        "value": {"type": "integer", "min": 0, "max": 100, "required": True},
    },
}

# Register and generate
registry = get_registry()
registry.register_schema(MY_SCHEMA)

generator = TraditionalGenerator()
request = test_data_pb2.GenerateRequest(
    entity="my_entity",
    count=10
)

result = await generator.generate(request)
print(result.data)  # Your generated data!
```

**Use this when:**
- Testing custom schemas quickly
- One-off data generation
- Prototyping

---

### Method 2: Add to Codebase (Best for Permanent Schemas)

**Step 1:** Create `src/test_data_agent/schemas/entities/my_entity.py`:
```python
MY_ENTITY_SCHEMA = {
    "name": "my_entity",
    # ... fields ...
}
```

**Step 2:** Import in `src/test_data_agent/schemas/entities/__init__.py`:
```python
from .my_entity import MY_ENTITY_SCHEMA

__all__ = [..., "MY_ENTITY_SCHEMA"]
```

**Step 3:** Load in `src/test_data_agent/schemas/registry.py`:
```python
from test_data_agent.schemas.entities import (
    # ... existing schemas ...,
    MY_ENTITY_SCHEMA,
)

schemas = [..., MY_ENTITY_SCHEMA]
```

**Step 4:** Restart service & test:
```bash
python -m test_data_agent.main &

grpcurl -plaintext -d '{
  "entity": "my_entity",
  "count": 10
}' localhost:9091 testdata.v1.TestDataService/GenerateData | jq
```

**Use this when:**
- Schema will be used repeatedly
- Part of your core test suite
- Sharing with team via gRPC

---

### Method 3: gRPC with inline schema (Future feature)

**Not currently implemented**, but the proto could support:
```bash
grpcurl -plaintext -d '{
  "entity": "custom",
  "count": 10,
  "inline_schema": {
    "name": "custom",
    "fields": {...}
  }
}' localhost:9091 testdata.v1.TestDataService/GenerateData
```

**Use Python API (Method 1) instead for now.**

---

## 🎯 Schema Structure Reference

### Minimum Required Schema

```python
{
    "name": "entity_name",        # Required: snake_case identifier
    "domain": "domain_name",      # Required: categorization
    "description": "Description",  # Required: what it represents
    "fields": {                   # Required: field definitions
        "id": {
            "type": "string",     # Required: data type
            "required": True,     # Required: is mandatory?
        }
    }
}
```

### Full Schema with All Options

```python
{
    "name": "employee",
    "domain": "hr",
    "description": "Employee record",
    "fields": {
        "employee_id": {
            "type": "string",
            "format": "EMP-{year}-{random:5}",  # Pattern
            "required": True,
            "description": "Employee ID",
        },
        "department": {
            "type": "enum",
            "values": ["Eng", "Sales", "HR"],   # Fixed options
            "required": True,
        },
        "salary": {
            "type": "float",
            "min": 40000.0,                      # Min value
            "max": 250000.0,                     # Max value
            "required": True,
        },
        "is_active": {
            "type": "boolean",
            "default": True,                     # Default if not provided
            "required": False,                   # Optional field
        },
    },
    "coherence_rules": [                         # Optional: for LLM
        "salary > 0",
        "hire_date < current_date",
    ],
}
```

---

## 📊 Supported Field Types

| Type | Example Value | Constraints |
|------|---------------|-------------|
| `string` | "John Doe" | min_length, max_length, regex, format |
| `integer` | 42 | min, max |
| `float` | 19.99 | min, max |
| `boolean` | true | default |
| `datetime` | "2025-12-13T10:30:00Z" | format (iso8601) |
| `enum` | "Active" | values (list of allowed) |
| `array` | [1, 2, 3] | item_schema, min_items, max_items |
| `object` | {"key": "val"} | fields (nested schema) |

---

## 🚀 Quick Test Workflow

1. **Create schema** (see examples in `/tmp/CUSTOM_SCHEMA_GUIDE.md`)
2. **Run example**:
   ```bash
   python /tmp/example_custom_schema.py
   ```
3. **Check output**:
   ```bash
   cat /tmp/employees.json | jq | head -50
   ```
4. **Modify & rerun**

---

## 💡 Tips

✅ **DO:**
- Start with Method 1 (Python API) for testing
- Use descriptive field names (`employee_id` not `id`)
- Set min/max constraints for numbers
- Use enums for fixed values
- Add field descriptions

❌ **DON'T:**
- Forget to set `required: True/False`
- Use overly generic names
- Skip validation constraints
- Forget to restart service (Method 2)

---

## 📚 Full Documentation

- **Complete Guide:** `/tmp/CUSTOM_SCHEMA_GUIDE.md`
- **Working Example:** `/tmp/example_custom_schema.py`
- **Example Schemas:** `src/test_data_agent/schemas/entities/`

---

## 🎓 Next Steps

1. **Try the example:**
   ```bash
   python /tmp/example_custom_schema.py
   ```

2. **View generated data:**
   ```bash
   cat /tmp/employees.json | jq '.[0]'
   ```

3. **Modify the schema** in the example file and run again

4. **Add your own schema** following Method 1 or Method 2

5. **Test with LLM/RAG paths** once working

---

**Happy schema building!** 🚀
