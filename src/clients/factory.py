"""Client factory for automatic provider detection."""

from src.clients.base import ModelClient
from src.clients.gemini import GeminiClient
from src.clients.openai import OpenAIClient


def get_client(model: str) -> ModelClient:
    """
    Get the appropriate client for a model based on its name.
    
    Args:
        model: Model name (e.g., "gpt-4o", "gemini-1.5-flash")
        
    Returns:
        ModelClient instance configured for the model
        
    Model prefix detection:
        - gemini-* → GeminiClient
        - gpt-*, o1-*, text-*, others → OpenAIClient
    """
    if model.startswith("gemini-"):
        return GeminiClient(model=model)
    else:
        # Default to OpenAI for gpt-*, o1-*, and any other models
        return OpenAIClient(model=model)
