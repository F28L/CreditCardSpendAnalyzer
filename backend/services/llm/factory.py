"""LLM provider factory."""
from .base import BaseLLMProvider
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from config import settings


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory function to instantiate the correct LLM provider based on settings.

    Returns:
        Instance of BaseLLMProvider (either OllamaProvider or OpenAIProvider)

    Raises:
        ValueError: If unknown provider is specified
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "ollama":
        return OllamaProvider(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL)
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        return OpenAIProvider(api_key=settings.OPENAI_API_KEY, model=settings.OPENAI_MODEL)
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. Must be 'ollama' or 'openai'"
        )
