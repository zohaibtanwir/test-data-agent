"""Prompt templates for different generation scenarios."""

# Template for general data generation
GENERAL_TEMPLATE = """Generate {count} test data records for the {domain} domain.

CONTEXT:
{context}

SCHEMA:
{schema}

CONSTRAINTS:
{constraints}

SCENARIOS:
{scenarios}

Generate exactly {count} records distributed across the scenarios as specified. Output valid JSON array only."""

# Template with RAG examples
RAG_TEMPLATE = """Generate {count} test data records for the {domain} domain.

CONTEXT:
{context}

REFERENCE EXAMPLES (from similar successful test data):
Study these examples to understand the expected patterns and quality:
{rag_examples}

SCHEMA:
{schema}

CONSTRAINTS:
{constraints}

Generate data that matches the quality and patterns shown in the examples while conforming to the schema. Output valid JSON array only."""

# Template for edge cases
EDGE_CASE_TEMPLATE = """Generate {count} EDGE CASE test data records designed to stress-test the system.

CONTEXT:
{context}

HISTORICAL DEFECT PATTERNS (from past bugs):
These data patterns have caused bugs before. Generate similar data to catch regressions:
{defect_patterns}

EDGE CASES TO INCLUDE:
- Boundary values (min, max, just above/below limits)
- Special characters (unicode, emojis, SQL injection patterns)
- Empty/null values where allowed
- Timezone edge cases (midnight, DST boundaries)
- Very long strings at max length
- Decimal precision edge cases

SCHEMA:
{schema}

Each record should target a specific edge case. Include '_edge_case_type' field describing what edge case it tests. Output valid JSON array only."""

# Template for coherent entities (carts, orders)
COHERENT_TEMPLATE = """Generate a COHERENT {entity_type} with logically related items.

CONTEXT:
{context}

COHERENCE REQUIREMENTS:
- Items must logically belong together (what a real customer would buy)
- Consider: shopping occasion, category affinity, complementary products
- Amounts must be mathematically consistent (subtotal + tax = total)
- Dates must be chronologically valid (created < modified < completed)

COHERENT SET EXAMPLES:
- Fitness: Running shoes + Athletic socks + Water bottle + Fitness tracker
- Date night: Dress + Heels + Clutch + Jewelry
- Home refresh: Bedding set + Pillows + Throw blanket + Candles
- Baby shower gift: Onesies + Blanket + Stuffed animal + Card

SCHEMA:
{schema}

Include '_shopping_occasion' field describing the coherent theme. Output valid JSON only."""

# Template for text content (reviews, comments)
TEXT_CONTENT_TEMPLATE = """Generate {count} realistic {content_type} entries.

CONTEXT:
{context}

TEXT QUALITY REQUIREMENTS:
- Write like a real customer, not a marketer or AI
- Include natural imperfections (casual grammar, abbreviations)
- Vary length and detail level across entries
- Reference specific product attributes when relevant
- Include emotional language where appropriate

SENTIMENT DISTRIBUTION:
{sentiment_distribution}

SCHEMA:
{schema}

Include '_sentiment' field (positive/negative/neutral). Output valid JSON array only."""
