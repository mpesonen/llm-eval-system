from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass
class EvalResult:
    id: str
    suite_id: str
    case_id: str
    model: str
    prompt: str
    response: str
    passed: bool
    score: float
    reasons: list[str]
    timestamp: datetime


@dataclass
class EvalRun:
    id: str
    suite_id: str
    model: str
    timestamp: datetime
    results: list[EvalResult]


class ResultStore(Protocol):
    def save_run(self, run: EvalRun) -> None: ...

    def get_run(self, run_id: str) -> EvalRun | None: ...

    def list_runs(self, suite_id: str | None = None) -> list[EvalRun]: ...
