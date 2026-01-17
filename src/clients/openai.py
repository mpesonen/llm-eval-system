from langsmith import traceable, wrappers
from openai import OpenAI

from src.clients.base import ModelRequest, ModelResponse


class OpenAIClient:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.default_model = model
        self._client = wrappers.wrap_openai(OpenAI())

    @traceable
    def generate(self, request: ModelRequest) -> ModelResponse:
        model = request.model or self.default_model

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        completion = self._client.chat.completions.create(
            model=model,
            messages=messages,
        )

        return ModelResponse(
            content=completion.choices[0].message.content or "",
            model=model,
            usage={
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
            },
            finish_reason=completion.choices[0].finish_reason,
        )
