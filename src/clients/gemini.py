"""Google Gemini client implementation using google-genai SDK."""

import os

from google import genai
from google.genai import types
from langsmith import traceable

from src.clients.base import ModelRequest, ModelResponse


class GeminiClient:
    """Client for Google Gemini models."""

    def __init__(self, model: str = "gemini-1.5-flash"):
        self.default_model = model
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        self.client = genai.Client(api_key=api_key)

    @traceable
    def generate(self, request: ModelRequest) -> ModelResponse:
        model_name = request.model or self.default_model

        # Build the config with optional system instruction
        config = types.GenerateContentConfig()
        if request.system_prompt:
            config = types.GenerateContentConfig(
                system_instruction=request.system_prompt
            )

        # Generate response
        response = self.client.models.generate_content(
            model=model_name,
            contents=request.prompt,
            config=config,
        )

        # Extract usage metadata if available
        usage = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count,
            }

        # Get finish reason
        finish_reason = "stop"
        if response.candidates and response.candidates[0].finish_reason:
            finish_reason = str(response.candidates[0].finish_reason).lower()

        return ModelResponse(
            content=response.text,
            model=model_name,
            usage=usage,
            finish_reason=finish_reason,
        )
