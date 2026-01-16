from dataclasses import dataclass
from typing import Protocol


@dataclass
class ModelRequest:
    prompt: str
    model: str | None = None


@dataclass
class ModelResponse:
    content: str
    model: str
    usage: dict
    finish_reason: str


class ModelClient(Protocol):
    def generate(self, request: ModelRequest) -> ModelResponse: ...
