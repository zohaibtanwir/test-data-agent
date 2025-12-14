"""Unit tests for Claude API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from anthropic import RateLimitError, APIError, APITimeoutError
from anthropic.types import Message, Usage
from anthropic.types.content_block import ContentBlock
from anthropic.types.text_block import TextBlock

from test_data_agent.clients.claude import ClaudeClient
from test_data_agent.config import load_settings


@pytest.fixture
def settings():
    """Fixture for test settings."""
    return load_settings(
        anthropic_api_key="test-api-key",
        claude_model="claude-sonnet-4-20250514",
        claude_max_tokens=4096,
        claude_temperature=0.7,
    )


@pytest.fixture
def claude_client(settings):
    """Fixture for Claude client."""
    return ClaudeClient(settings)


@pytest.fixture
def mock_message():
    """Fixture for mock Claude API message."""
    text_block = TextBlock(type="text", text="Generated response")

    return Message(
        id="msg_123",
        type="message",
        role="assistant",
        content=[text_block],
        model="claude-sonnet-4-20250514",
        stop_reason="end_turn",
        stop_sequence=None,
        usage=Usage(input_tokens=100, output_tokens=50),
    )


@pytest.mark.asyncio
async def test_generate_success(claude_client, mock_message):
    """Test successful generation."""
    with patch.object(claude_client, "_call_api", return_value=mock_message):
        response = await claude_client.generate(
            system="You are a helpful assistant",
            user="Generate test data",
        )

        assert response.content == "Generated response"
        assert response.tokens_used == 150  # 100 + 50
        assert response.model == "claude-sonnet-4-20250514"
        assert response.stop_reason == "end_turn"


@pytest.mark.asyncio
async def test_generate_retry_on_rate_limit(claude_client, mock_message):
    """Test retry on rate limit error."""
    # Create a mock RateLimitError that can be raised
    class MockRateLimitError(Exception):
        pass

    with patch.object(claude_client, "_call_api") as mock_call:
        with patch("test_data_agent.clients.claude.RateLimitError", MockRateLimitError):
            # First call raises rate limit, second succeeds
            mock_call.side_effect = [
                MockRateLimitError("Rate limit exceeded"),
                mock_message,
            ]

            response = await claude_client.generate(
                system="System",
                user="User",
            )

            assert response.content == "Generated response"
            assert mock_call.call_count == 2


@pytest.mark.asyncio
async def test_generate_retry_on_timeout(claude_client, mock_message):
    """Test retry on timeout error."""
    with patch.object(claude_client, "_call_api") as mock_call:
        # First call times out, second succeeds
        mock_call.side_effect = [
            APITimeoutError("Request timeout"),
            mock_message,
        ]

        response = await claude_client.generate(
            system="System",
            user="User",
        )

        assert response.content == "Generated response"
        assert mock_call.call_count == 2


@pytest.mark.asyncio
async def test_generate_exhausts_retries(claude_client):
    """Test that retries are exhausted on persistent rate limits."""
    # Create a mock RateLimitError that can be raised
    class MockRateLimitError(Exception):
        pass

    with patch.object(claude_client, "_call_api") as mock_call:
        with patch("test_data_agent.clients.claude.RateLimitError", MockRateLimitError):
            # All calls raise RateLimitError
            mock_call.side_effect = MockRateLimitError("Rate limit exceeded")

            with pytest.raises(MockRateLimitError):
                await claude_client.generate(system="System", user="User")

            # Should have tried 3 times (max_retries)
            assert mock_call.call_count == 3


@pytest.mark.asyncio
async def test_generate_no_retry_on_api_error(claude_client):
    """Test that API errors are not retried."""
    # Create a mock APIError that can be raised
    class MockAPIError(Exception):
        pass

    with patch.object(claude_client, "_call_api") as mock_call:
        with patch("test_data_agent.clients.claude.APIError", MockAPIError):
            mock_call.side_effect = MockAPIError("Invalid API key")

            with pytest.raises(MockAPIError):
                await claude_client.generate(system="System", user="User")

            # Should only try once
            assert mock_call.call_count == 1


@pytest.mark.asyncio
async def test_generate_json_parse(claude_client):
    """Test JSON parsing from Claude response."""
    json_response = '{"name": "test", "count": 42}'
    text_block = TextBlock(type="text", text=json_response)

    mock_message = Message(
        id="msg_123",
        type="message",
        role="assistant",
        content=[text_block],
        model="claude-sonnet-4-20250514",
        stop_reason="end_turn",
        stop_sequence=None,
        usage=Usage(input_tokens=100, output_tokens=50),
    )

    with patch.object(claude_client, "_call_api", return_value=mock_message):
        data = await claude_client.generate_json(
            system="Generate JSON",
            user="Create test data",
        )

        assert data == {"name": "test", "count": 42}


@pytest.mark.asyncio
async def test_generate_json_strips_markdown(claude_client):
    """Test that markdown code blocks are stripped."""
    json_with_markdown = """```json
{
  "name": "test",
  "count": 42
}
```"""
    text_block = TextBlock(type="text", text=json_with_markdown)

    mock_message = Message(
        id="msg_123",
        type="message",
        role="assistant",
        content=[text_block],
        model="claude-sonnet-4-20250514",
        stop_reason="end_turn",
        stop_sequence=None,
        usage=Usage(input_tokens=100, output_tokens=50),
    )

    with patch.object(claude_client, "_call_api", return_value=mock_message):
        data = await claude_client.generate_json(
            system="Generate JSON",
            user="Create test data",
        )

        assert data == {"name": "test", "count": 42}


@pytest.mark.asyncio
async def test_generate_json_invalid_raises_error(claude_client):
    """Test that invalid JSON raises ValueError."""
    text_block = TextBlock(type="text", text="This is not JSON")

    mock_message = Message(
        id="msg_123",
        type="message",
        role="assistant",
        content=[text_block],
        model="claude-sonnet-4-20250514",
        stop_reason="end_turn",
        stop_sequence=None,
        usage=Usage(input_tokens=100, output_tokens=50),
    )

    with patch.object(claude_client, "_call_api", return_value=mock_message):
        with pytest.raises(ValueError) as exc_info:
            await claude_client.generate_json(system="System", user="User")

        assert "Failed to parse JSON" in str(exc_info.value)
