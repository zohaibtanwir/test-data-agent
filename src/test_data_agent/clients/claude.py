"""Claude API client with retry logic."""

import asyncio
from dataclasses import dataclass

from anthropic import Anthropic, APIError, RateLimitError, APITimeoutError
from anthropic.types import Message

from test_data_agent.config import Settings
from test_data_agent.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ClaudeResponse:
    """Response from Claude API."""

    content: str
    tokens_used: int  # input + output tokens
    model: str
    stop_reason: str


class ClaudeClient:
    """Client for Claude API with retry logic."""

    def __init__(self, settings: Settings):
        """
        Initialize Claude client.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.max_retries = 3
        self.base_delay = 1.0  # seconds
        logger.info(
            "claude_client_initialized",
            model=settings.claude_model,
            max_tokens=settings.claude_max_tokens,
        )

    async def generate(
        self,
        system: str,
        user: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> ClaudeResponse:
        """
        Generate text with Claude.

        Args:
            system: System prompt
            user: User prompt
            max_tokens: Max tokens to generate (defaults to settings)
            temperature: Temperature (defaults to settings)

        Returns:
            ClaudeResponse with content and metadata

        Raises:
            APIError: On authentication or other API errors
        """
        max_tokens = max_tokens or self.settings.claude_max_tokens
        temperature = temperature if temperature is not None else self.settings.claude_temperature

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    "claude_api_call",
                    attempt=attempt + 1,
                    model=self.settings.claude_model,
                )

                # Make API call (synchronous, run in thread pool)
                message = await asyncio.to_thread(
                    self._call_api,
                    system=system,
                    user=user,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                # Extract content
                content = ""
                for block in message.content:
                    if hasattr(block, "text"):
                        content += block.text

                # Calculate tokens used
                tokens_used = message.usage.input_tokens + message.usage.output_tokens

                logger.info(
                    "claude_api_success",
                    tokens_used=tokens_used,
                    stop_reason=message.stop_reason,
                )

                return ClaudeResponse(
                    content=content,
                    tokens_used=tokens_used,
                    model=message.model,
                    stop_reason=message.stop_reason,
                )

            except RateLimitError:
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2**attempt)
                    logger.warning(
                        "claude_rate_limit",
                        attempt=attempt + 1,
                        retry_delay=delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("claude_rate_limit_exhausted")
                    raise

            except APITimeoutError:
                if attempt < self.max_retries - 1:
                    delay = self.base_delay * (2**attempt)
                    logger.warning(
                        "claude_timeout",
                        attempt=attempt + 1,
                        retry_delay=delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("claude_timeout_exhausted")
                    raise

            except APIError as e:
                # Don't retry on authentication or other API errors
                logger.error("claude_api_error", error=str(e))
                raise

        # Should not reach here
        raise APIError("Max retries exceeded")

    async def generate_json(
        self,
        system: str,
        user: str,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> dict:
        """
        Generate JSON response with Claude.

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
        import json
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
            logger.debug("claude_json_parsed", type=type(data).__name__)
            return data
        except json.JSONDecodeError as e:
            logger.error("claude_json_parse_error", error=str(e), content=content[:200])
            raise ValueError(f"Failed to parse JSON from Claude response: {e}")

    def _call_api(
        self,
        system: str,
        user: str,
        max_tokens: int,
        temperature: float,
    ) -> Message:
        """
        Make synchronous API call to Claude.

        Args:
            system: System prompt
            user: User prompt
            max_tokens: Max tokens
            temperature: Temperature

        Returns:
            Message from Claude API
        """
        return self.client.messages.create(
            model=self.settings.claude_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
