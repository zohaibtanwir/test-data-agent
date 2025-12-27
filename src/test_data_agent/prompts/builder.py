"""Prompt builder for dynamic LLM prompt construction."""

import json
from typing import Any

from test_data_agent.prompts.system import SYSTEM_PROMPT
from test_data_agent.prompts.templates import (
    GENERAL_TEMPLATE,
    RAG_TEMPLATE,
    EDGE_CASE_TEMPLATE,
    COHERENT_TEMPLATE,
    TEXT_CONTENT_TEMPLATE,
)


class PromptBuilder:
    """Builds prompts for LLM-based data generation."""

    def build_prompt(
        self,
        request: Any,
        schema_dict: dict | None,
        rag_context: list[dict] | None = None,
    ) -> tuple[str, str]:
        """Build system and user prompts for generation.

        Args:
            request: GenerateRequest proto message
            schema_dict: Schema dictionary from registry (can be None)
            rag_context: Optional RAG examples

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        # Select template based on request characteristics
        template = self.select_template(request, rag_context)

        # Format schema
        schema_str = self.format_schema(schema_dict)

        # Format constraints
        constraints_str = self.format_constraints(request.constraints)

        # Format scenarios
        scenarios_str = self.format_scenarios(request.scenarios)

        # Build user prompt from template
        user_prompt = template.format(
            count=request.count,
            domain=request.domain,
            entity=request.entity,
            entity_type=request.entity,
            content_type=f"{request.entity}s",
            context=request.context or "No specific context provided.",
            schema=schema_str,
            constraints=constraints_str,
            scenarios=scenarios_str,
            rag_examples=self.format_rag_examples(rag_context) if rag_context else "",
            defect_patterns=self.format_rag_examples(rag_context) if rag_context else "",
            sentiment_distribution="Mixed: 60% positive, 30% neutral, 10% negative",
        )

        return (SYSTEM_PROMPT, user_prompt)

    def select_template(self, request: Any, rag_context: list[dict] | None = None) -> str:
        """Select appropriate template based on request characteristics.

        Args:
            request: GenerateRequest proto message
            rag_context: Optional RAG examples

        Returns:
            Template string
        """
        hints = [h.lower() for h in request.hints]

        # Edge case template
        if request.defect_triggering or "edge_case" in hints or "defect" in hints:
            return EDGE_CASE_TEMPLATE

        # Coherent template for carts/orders
        if request.entity in ["cart", "order"] and ("coherent" in hints or "realistic" in hints):
            return COHERENT_TEMPLATE

        # Text content template for reviews/comments
        if request.entity in ["review", "comment", "feedback"]:
            return TEXT_CONTENT_TEMPLATE

        # RAG template if context provided
        if rag_context and len(rag_context) > 0:
            return RAG_TEMPLATE

        # Default general template
        return GENERAL_TEMPLATE

    def format_schema(self, schema_dict: dict | None) -> str:
        """Format schema into readable string for prompt.

        Args:
            schema_dict: Schema dictionary (can be None)

        Returns:
            Formatted schema string
        """
        # Handle None or empty schema_dict
        if not schema_dict:
            return "No specific schema provided. Generate data based on entity name and context."

        lines = []
        lines.append(f"Entity: {schema_dict.get('name', 'unknown')}")
        lines.append(f"Domain: {schema_dict.get('domain', 'unknown')}")
        lines.append(f"Description: {schema_dict.get('description', '')}")
        lines.append("\nFields:")

        fields = schema_dict.get("fields", {})
        for field_name, field_info in fields.items():
            required = " (REQUIRED)" if field_info.get("required", False) else ""
            field_type = field_info.get("type", "string")
            description = field_info.get("description", "")
            format_str = field_info.get("format", "")

            field_line = f"  - {field_name}: {field_type}{required}"
            if description:
                field_line += f" - {description}"
            if format_str:
                field_line += f" (format: {format_str})"

            lines.append(field_line)

            # Handle nested fields
            if "nested_schema" in field_info:
                nested = field_info["nested_schema"]
                for nested_name, nested_info in nested.items():
                    nested_type = nested_info.get("type", "string")
                    lines.append(f"    - {nested_name}: {nested_type}")

        # Add coherence rules if present
        if "coherence_rules" in schema_dict:
            lines.append("\nCoherence Rules:")
            for rule in schema_dict["coherence_rules"]:
                lines.append(f"  - {rule}")

        return "\n".join(lines)

    def format_constraints(self, constraints: Any) -> str:
        """Format constraints into readable string.

        Args:
            constraints: Constraints proto message

        Returns:
            Formatted constraints string
        """
        if not constraints or not constraints.field_constraints:
            return "No specific constraints."

        lines = []
        for field_name, constraint in constraints.field_constraints.items():
            parts = [f"{field_name}:"]

            if constraint.HasField("min"):
                parts.append(f"min={constraint.min}")
            if constraint.HasField("max"):
                parts.append(f"max={constraint.max}")
            if constraint.HasField("min_length"):
                parts.append(f"min_length={constraint.min_length}")
            if constraint.HasField("max_length"):
                parts.append(f"max_length={constraint.max_length}")
            if constraint.enum_values:
                parts.append(f"values={list(constraint.enum_values)}")
            if constraint.HasField("regex"):
                parts.append(f"pattern={constraint.regex}")
            if constraint.HasField("format"):
                parts.append(f"format={constraint.format}")

            lines.append("  - " + " ".join(parts))

        return "\n".join(lines) if lines else "No specific constraints."

    def format_scenarios(self, scenarios: list[Any]) -> str:
        """Format scenarios into readable string.

        Args:
            scenarios: List of Scenario proto messages

        Returns:
            Formatted scenarios string
        """
        if not scenarios:
            return "Generate all records with default scenario."

        lines = []
        for scenario in scenarios:
            parts = [f"{scenario.name}: {scenario.count} records"]
            if scenario.description:
                parts.append(f"- {scenario.description}")
            if scenario.overrides:
                overrides = ", ".join(f"{k}={v}" for k, v in scenario.overrides.items())
                parts.append(f"(overrides: {overrides})")
            lines.append("  - " + " ".join(parts))

        return "\n".join(lines)

    def format_rag_examples(self, examples: list[dict] | None) -> str:
        """Format RAG examples into readable string.

        Args:
            examples: List of example data dicts

        Returns:
            Formatted examples string
        """
        if not examples:
            return "No examples provided."

        lines = []
        for i, example in enumerate(examples[:5]):  # Limit to 5 examples
            lines.append(f"Example {i + 1}:")
            lines.append(json.dumps(example, indent=2))
            lines.append("")

        return "\n".join(lines)
