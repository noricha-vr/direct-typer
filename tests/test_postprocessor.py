"""Tests for PostProcessor module."""

import pytest
from unittest.mock import MagicMock, patch

from direct_typer.postprocessor import PostProcessor


class TestPostProcessorInit:
    """Test PostProcessor initialization."""

    @patch("direct_typer.postprocessor.OpenAI")
    @patch("os.getenv")
    def test_init_with_api_key(self, mock_getenv, mock_openai):
        """Test initialization with explicit API key."""
        processor = PostProcessor(api_key="test-api-key")

        mock_openai.assert_called_once_with(
            base_url="https://openrouter.ai/api/v1",
            api_key="test-api-key",
        )

    @patch("direct_typer.postprocessor.OpenAI")
    @patch("os.getenv")
    def test_init_with_env_var(self, mock_getenv, mock_openai):
        """Test initialization with environment variable."""
        mock_getenv.return_value = "env-api-key"

        processor = PostProcessor()

        mock_getenv.assert_called_with("OPENROUTER_API_KEY")
        mock_openai.assert_called_once_with(
            base_url="https://openrouter.ai/api/v1",
            api_key="env-api-key",
        )

    @patch("direct_typer.postprocessor.OpenAI")
    @patch("os.getenv")
    def test_init_without_api_key_raises(self, mock_getenv, mock_openai):
        """Test initialization without API key raises ValueError."""
        mock_getenv.return_value = None

        with pytest.raises(ValueError) as exc_info:
            PostProcessor()

        assert "OPENROUTER_API_KEY is not set" in str(exc_info.value)

    def test_model_constant(self):
        """Test MODEL constant is set correctly."""
        assert PostProcessor.MODEL == "google/gemini-2.5-flash-lite"


class TestPostProcessorProcess:
    """Test PostProcessor.process method."""

    @patch("direct_typer.postprocessor.OpenAI")
    @patch("os.getenv", return_value="test-api-key")
    def test_process_returns_processed_text(self, mock_getenv, mock_openai):
        """Test process returns processed text from LLM."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "  processed text  "
        mock_client.chat.completions.create.return_value = mock_response

        processor = PostProcessor()
        result = processor.process("input text")

        assert result == "processed text"
        mock_client.chat.completions.create.assert_called_once()

        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == "google/gemini-2.5-flash-lite"
        assert len(call_args.kwargs["messages"]) == 2
        assert call_args.kwargs["messages"][0]["role"] == "system"
        assert call_args.kwargs["messages"][1]["role"] == "user"
        assert call_args.kwargs["messages"][1]["content"] == "input text"

    @patch("direct_typer.postprocessor.OpenAI")
    @patch("os.getenv", return_value="test-api-key")
    def test_process_empty_string_returns_empty(self, mock_getenv, mock_openai):
        """Test process returns empty string for empty input."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        processor = PostProcessor()
        result = processor.process("")

        assert result == ""
        mock_client.chat.completions.create.assert_not_called()

    @patch("direct_typer.postprocessor.OpenAI")
    @patch("os.getenv", return_value="test-api-key")
    def test_process_whitespace_only_returns_empty(self, mock_getenv, mock_openai):
        """Test process returns empty string for whitespace-only input."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        processor = PostProcessor()
        result = processor.process("   \n\t  ")

        assert result == ""
        mock_client.chat.completions.create.assert_not_called()
