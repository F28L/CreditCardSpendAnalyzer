"""Tests for LLM providers."""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from services.llm.ollama_provider import OllamaProvider
from services.llm.openai_provider import OpenAIProvider
from services.llm.factory import get_llm_provider


@pytest.mark.asyncio
async def test_ollama_generate_insight():
    """Test Ollama insight generation."""
    with patch("services.llm.ollama_provider.ollama.chat") as mock_chat:
        mock_chat.return_value = {
            "message": {"content": "You spent $500 on dining out this month."}
        }

        provider = OllamaProvider(model="llama3")
        transactions = [
            {"date": "2024-01-15", "merchant_name": "Restaurant", "amount": 50.0},
            {"date": "2024-01-20", "merchant_name": "Coffee Shop", "amount": 5.0},
        ]

        result = await provider.generate_insight("Analyze spending", transactions)

        assert "500" in result
        assert "dining" in result.lower()
        mock_chat.assert_called_once()


@pytest.mark.asyncio
async def test_ollama_categorize_transaction():
    """Test Ollama transaction categorization."""
    with patch("services.llm.ollama_provider.ollama.chat") as mock_chat:
        mock_chat.return_value = {"message": {"content": "Dining Out"}}

        provider = OllamaProvider(model="llama3")
        transaction = {
            "merchant_name": "Starbucks",
            "amount": 5.50,
            "description": "Coffee",
        }

        category = await provider.categorize_transaction(transaction)

        assert category == "Dining Out"
        mock_chat.assert_called_once()


@pytest.mark.asyncio
async def test_ollama_detect_reimbursement():
    """Test Ollama reimbursement detection."""
    with patch("services.llm.ollama_provider.ollama.chat") as mock_chat:
        mock_chat.return_value = {
            "message": {
                "content": '{"is_reimbursement": true, "confidence": 0.9, "reasoning": "Contains keyword reimburse"}'
            }
        }

        provider = OllamaProvider(model="llama3")
        transaction = {
            "merchant_name": "Venmo",
            "amount": 50.0,
            "description": "Reimburse for dinner",
        }

        is_reimbursement, confidence = await provider.detect_reimbursement(transaction)

        assert is_reimbursement is True
        assert confidence == 0.9


@pytest.mark.asyncio
async def test_ollama_detect_reimbursement_fallback():
    """Test Ollama reimbursement detection fallback to keyword matching."""
    with patch("services.llm.ollama_provider.ollama.chat") as mock_chat:
        # Simulate JSON parse error
        mock_chat.return_value = {"message": {"content": "invalid json"}}

        provider = OllamaProvider(model="llama3")
        transaction = {
            "merchant_name": "Venmo",
            "amount": 50.0,
            "description": "paid back for dinner",
        }

        is_reimbursement, confidence = await provider.detect_reimbursement(transaction)

        # Should fall back to keyword detection
        assert is_reimbursement is True
        assert confidence == 0.7


@pytest.mark.asyncio
async def test_openai_generate_insight():
    """Test OpenAI insight generation."""
    with patch("services.llm.openai_provider.AsyncOpenAI") as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="You spent $500 on dining out."))
        ]
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(api_key="test-key", model="gpt-4o-mini")
        transactions = [
            {"date": "2024-01-15", "merchant_name": "Restaurant", "amount": 50.0}
        ]

        result = await provider.generate_insight("Analyze spending", transactions)

        assert "500" in result
        mock_instance.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_openai_categorize_transaction():
    """Test OpenAI transaction categorization."""
    with patch("services.llm.openai_provider.AsyncOpenAI") as MockClient:
        mock_instance = MockClient.return_value
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Dining Out"))]
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(api_key="test-key", model="gpt-4o-mini")
        transaction = {
            "merchant_name": "Starbucks",
            "amount": 5.50,
            "description": "Coffee",
        }

        category = await provider.categorize_transaction(transaction)

        assert category == "Dining Out"
        mock_instance.chat.completions.create.assert_called_once()


def test_llm_factory_ollama():
    """Test LLM factory with Ollama provider."""
    with patch("services.llm.factory.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "ollama"
        mock_settings.OLLAMA_MODEL = "llama3"
        mock_settings.OLLAMA_BASE_URL = "http://localhost:11434"

        provider = get_llm_provider()

        assert isinstance(provider, OllamaProvider)
        assert provider.model == "llama3"


def test_llm_factory_openai():
    """Test LLM factory with OpenAI provider."""
    with patch("services.llm.factory.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = "test-key"
        mock_settings.OPENAI_MODEL = "gpt-4o-mini"

        provider = get_llm_provider()

        assert isinstance(provider, OpenAIProvider)
        assert provider.model == "gpt-4o-mini"


def test_llm_factory_invalid_provider():
    """Test LLM factory with invalid provider."""
    with patch("services.llm.factory.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "invalid"

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            get_llm_provider()


def test_llm_factory_openai_missing_key():
    """Test LLM factory with OpenAI but missing API key."""
    with patch("services.llm.factory.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "openai"
        mock_settings.OPENAI_API_KEY = ""

        with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
            get_llm_provider()
