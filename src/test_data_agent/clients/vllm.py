"""vLLM client using OpenAI-compatible API."""

import asyncio
import json
from dataclasses import dataclass

from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError

from test_data_agent.config import Settings
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class VLLMResponse:
    """Response from vLLM API."""

    content: str
    tokens_used: int  # Approximate, vLLM may not return exact counts
    model: str
    stop_reason: str


class VLLMClient:
    """Client for vLLM using OpenAI-compatible API."""

    def __init__(self, settings: Settings):
        """Initialize vLLM client.

        Args:
            settings: Application settings with vLLM config
        """
        self.settings = settings
        self.client = AsyncOpenAI(
            base_url=settings.vllm_base_url,
            api_key="dummy",  # vLLM doesn't require real API key
        )
        self.max_retries = 3
        self.base_delay = 1.0  # seconds
        logger.info(
            "vllm_client_initialized",
            base_url=settings.vllm_base_url,
            model=settings.vllm_model,
        )

    async def generate(
        self,
        system: str,
        user: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> VLLMResponse:
        """Generate text with vLLM.

        Args:
            system: System prompt
            user: User prompt
            max_tokens: Max tokens to generate
            temperature: Temperature (defaults to settings)

        Returns:
            VLLMResponse with content and metadata

        Raises:
            APIError: On API errors
        """
        max_tokens = max_tokens or self.settings.claude_max_tokens
        temperature = temperature if temperature is not None else self.settings.claude_temperature

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    "vllm_api_call",
                    attempt=attempt + 1,
                    model=self.settings.vllm_model,
                )

                # vLLM uses OpenAI-compatible chat completions API
                response = await self.client.chat.completions.create(
                    model=self.settings.vllm_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                choice = response.choices[0]
                content = choice.message.content or ""

                # vLLM may not always return usage info
                tokens_used = 0
                if response.usage:
                    tokens_used = response.usage.prompt_tokens + response.usage.completion_tokens

                logger.info(
                    "vllm_api_success",
                    tokens_used=tokens_used,
                    finish_reason=choice.finish_reason,
                )

                return VLLMResponse(
                    content=content,
                    tokens_used=tokens_used,
                    model=self.settings.vllm_model,
                    stop_reason=choice.finish_reason or "stop",
                )

            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2**attempt)
                    logger.warning(
                        "vllm_rate_limit",
                        attempt=attempt + 1,
                        retry_delay=delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("vllm_rate_limit_exhausted")
                    raise

            except APITimeoutError as e:
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2**attempt)
                    logger.warning(
                        "vllm_timeout",
                        attempt=attempt + 1,
                        retry_delay=delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("vllm_timeout_exhausted")
                    raise

            except APIError as e:
                logger.error("vllm_api_error", error=str(e))
                raise

            except Exception as e:
                logger.error("vllm_unexpected_error", error=str(e), type=type(e).__name__)
                raise

        raise APIError("Max retries exceeded")

    async def generate_json(
        self,
        system: str,
        user: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> dict:
        """Generate JSON response with vLLM.

        Args:
            system: System prompt
            user: User prompt
            max_tokens: Max tokens to generate
            temperature: Temperature

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If response is not valid JSON
            APIError: On API errors
        """
        response = await self.generate(system, user, max_tokens, temperature)

        # Parse JSON from response
        import re

        content = response.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            # Extract content between ```json and ```
            match = re.search(r"```(?:json)?\s*(.*?)\s*```", content, re.DOTALL)
            if match:
                content = match.group(1).strip()

        try:
            data = json.loads(content)
            logger.debug("vllm_json_parsed", type=type(data).__name__)
            return data
        except json.JSONDecodeError as e:
            logger.error("vllm_json_parse_error", error=str(e), content=content[:200])
            raise ValueError(f"Failed to parse JSON from vLLM response: {e}")
