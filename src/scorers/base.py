from dataclasses import dataclass
from typing import Protocol


@dataclass
class ScoreResult:
    passed: bool
    score: float  # 0.0 to 1.0
    reasons: list[str]


class Scorer(Protocol):
    def score(self, prompt: str, response: str, expected: dict) -> ScoreResult: ...
