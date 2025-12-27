"""LLM-based data generator using Claude or vLLM."""

import json
import time

from test_data_agent.generators.base import BaseGenerator, GenerationResult
from test_data_agent.clients.claude import ClaudeClient
from test_data_agent.clients.vllm import VLLMClient
from test_data_agent.prompts.builder import PromptBuilder
from test_data_agent.validators.constraint import ConstraintValidator
from test_data_agent.proto import test_data_pb2
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


class LLMGenerator(BaseGenerator):
    """Generator that uses LLM (Claude or vLLM) for intelligent data generation."""

    def __init__(
        self,
        claude_client: ClaudeClient,
        vllm_client: VLLMClient | None,
        prompt_builder: PromptBuilder,
        constraint_validator: ConstraintValidator,
    ):
        """Initialize LLM generator.

        Args:
            claude_client: Primary Claude API client
            vllm_client: Optional fallback vLLM client
            prompt_builder: Prompt builder for formatting prompts
            constraint_validator: Validator for checking generated data
        """
        self.claude_client = claude_client
        self.vllm_client = vllm_client
        self.prompt_builder = prompt_builder
        self.constraint_validator = constraint_validator
        self.max_retries = 2  # Retry on parse failure

    async def generate(
        self,
        request: test_data_pb2.GenerateRequest,
        context: dict | None = None,
    ) -> GenerationResult:
        """Generate data using LLM.

        Args:
            request: Generate data request
            context: Optional context (e.g., schema_dict, rag_examples)

        Returns:
            GenerationResult with generated data and metadata
        """
        start_time = time.time()
        schema_dict = context.get("schema_dict", {}) if context else {}
        rag_examples = context.get("rag_examples") if context else None

        # Build prompts
        system_prompt, user_prompt = self.prompt_builder.build_prompt(
            request, schema_dict, rag_examples
        )

        logger.info(
            "llm_generate_start",
            request_id=request.request_id,
            count=request.count,
            entity=request.entity,
        )

        # Try to generate with retries
        for attempt in range(self.max_retries + 1):
            try:
                # Try Claude first
                logger.debug("calling_claude_api", request_id=request.request_id)
                response = await self.claude_client.generate_json(
                    system=system_prompt,
                    user=user_prompt,
                )
                logger.debug(
                    "claude_api_returned",
                    request_id=request.request_id,
                    response_type=type(response).__name__,
                )

                # Parse and validate
                logger.debug("starting_parse_validate", request_id=request.request_id)
                data = self._parse_and_validate(response, schema_dict, request)
                logger.debug(
                    "parse_validate_complete", request_id=request.request_id, record_count=len(data)
                )

                duration = time.time() - start_time

                logger.info(
                    "llm_generate_success",
                    request_id=request.request_id,
                    records=len(data),
                    duration=duration,
                )

                return GenerationResult(
                    data=data,
                    metadata={
                        "generation_path": "llm",
                        "llm_provider": "claude",
                        "tokens_used": 0,  # Claude client handles this
                        "generation_time_ms": duration * 1000,
                        "coherence_score": 0.0,  # Will be calculated by coherence scorer
                        "attempts": attempt + 1,
                    },
                )

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    "llm_parse_error",
                    request_id=request.request_id,
                    attempt=attempt + 1,
                    error=str(e),
                )

                if attempt < self.max_retries:
                    # Retry with stricter prompt
                    user_prompt = self._make_stricter_prompt(user_prompt, schema_dict)
                    continue
                else:
                    # All retries exhausted, try fallback
                    if self.vllm_client:
                        logger.info("llm_fallback_to_vllm", request_id=request.request_id)
                        return await self._generate_with_vllm(
                            request, system_prompt, user_prompt, schema_dict, start_time
                        )
                    raise

            except Exception as e:
                logger.error(
                    "llm_generate_error",
                    request_id=request.request_id,
                    error=str(e),
                    type=type(e).__name__,
                )

                # Try fallback
                if self.vllm_client and attempt == 0:
                    logger.info("llm_fallback_to_vllm_on_error", request_id=request.request_id)
                    return await self._generate_with_vllm(
                        request, system_prompt, user_prompt, schema_dict, start_time
                    )
                raise

        # Should not reach here
        raise ValueError(f"Failed to generate data after {self.max_retries + 1} attempts")

    async def _generate_with_vllm(
        self,
        request: test_data_pb2.GenerateRequest,
        system_prompt: str,
        user_prompt: str,
        schema_dict: dict,
        start_time: float,
    ) -> GenerationResult:
        """Generate with vLLM fallback.

        Args:
            request: Generate data request
            system_prompt: System prompt
            user_prompt: User prompt
            schema_dict: Schema dictionary
            start_time: Start time for duration calculation

        Returns:
            GenerationResult
        """
        try:
            response = await self.vllm_client.generate_json(
                system=system_prompt,
                user=user_prompt,
            )

            data = self._parse_and_validate(response, schema_dict, request)
            duration = time.time() - start_time

            logger.info(
                "vllm_generate_success",
                request_id=request.request_id,
                records=len(data),
                duration=duration,
            )

            return GenerationResult(
                data=data,
                metadata={
                    "generation_path": "llm",
                    "llm_provider": "vllm",
                    "tokens_used": 0,
                    "generation_time_ms": duration * 1000,
                    "coherence_score": 0.0,
                },
            )
        except Exception as e:
            logger.error("vllm_generate_error", error=str(e))
            raise

    def _parse_and_validate(
        self, response: dict | list, schema_dict: dict, request: test_data_pb2.GenerateRequest
    ) -> list[dict]:
        """Parse and validate LLM response.

        Args:
            response: JSON response from LLM
            schema_dict: Schema dictionary
            request: Original request

        Returns:
            List of validated records

        Raises:
            ValueError: If response is invalid
        """
        logger.debug("parse_validate_start", response_type=type(response).__name__)

        # Ensure response is a list
        if isinstance(response, dict):
            # If LLM returned single object, wrap in list
            data = [response]
        elif isinstance(response, list):
            data = response
        else:
            raise ValueError(f"Invalid response type: {type(response)}")

        logger.debug("parse_validate_list_check", data_len=len(data))

        # Validate each record
        for idx, record in enumerate(data):
            logger.debug("validating_record", idx=idx, record_type=type(record).__name__)
            if not isinstance(record, dict):
                raise ValueError(f"Invalid record type: {type(record)}")

        logger.debug("parse_validate_adding_metadata")
        # Add metadata fields
        data = self._add_metadata_fields(data)

        logger.debug("llm_parsed_records", count=len(data))

        return data

    def _make_stricter_prompt(self, original_prompt: str, schema_dict: dict) -> str:
        """Make prompt stricter to improve JSON parsing success.

        Args:
            original_prompt: Original user prompt
            schema_dict: Schema dictionary

        Returns:
            Stricter prompt
        """
        stricter = (
            original_prompt
            + """\n
IMPORTANT: Output ONLY valid JSON array, no other text.

Example format:
[
  {
    "field1": "value1",
    "field2": 123,
    "_scenario": "default",
    "_index": 0
  },
  {
    "field1": "value2",
    "field2": 456,
    "_scenario": "default",
    "_index": 1
  }
]

Do not include markdown code blocks, explanations, or any other text. Only the JSON array.
"""
        )
        return stricter

    def supports(self, request: test_data_pb2.GenerateRequest) -> bool:
        """Check if LLM generator can handle this request.

        Args:
            request: Generate data request

        Returns:
            True if LLM should be used
        """
        hints = [h.lower() for h in request.hints]

        # Use LLM if:
        # - Context is provided
        # - "realistic" or "coherent" in hints
        # - Entity has text fields (review, comment)
        # - Entity is cart/order (needs coherence)
        # - Scenario descriptions provided

        if request.context:
            return True

        if any(hint in hints for hint in ["realistic", "coherent", "intelligent"]):
            return True

        if request.entity in ["review", "comment", "feedback", "description"]:
            return True

        if request.entity in ["cart", "order"] and "coherent" in hints:
            return True

        if any(s.description for s in request.scenarios):
            return True

        return False

    async def generate_stream(
        self,
        request: test_data_pb2.GenerateRequest,
        batch_size: int = 50,
        context: dict | None = None,
    ):
        """Stream LLM-generated records in batches.

        Args:
            request: Generate data request
            batch_size: Number of records per batch
            context: Optional context

        Yields:
            GenerationResult for each batch
        """
        # Use default implementation from BaseGenerator
        result = await self.generate(request, context)

        # Yield in batches
        for i in range(0, len(result.data), batch_size):
            batch = result.data[i : i + batch_size]
            yield GenerationResult(
                data=batch,
                metadata={
                    **result.metadata,
                    "batch_index": i // batch_size,
                    "batch_size": len(batch),
                },
            )
