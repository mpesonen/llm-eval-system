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
    system_prompt_name: str | None = None
    system_prompt_version: str | None = None


@dataclass
class EvalRun:
    id: str
    suite_id: str
    model: str
    timestamp: datetime
    results: list[EvalResult]
    system_prompt_name: str | None = None
    system_prompt_version: str | None = None
    revision: int | None = None  # Global sequential revision number
    git_commit_hash: str | None = None  # Auto-detected git commit


class ResultStore(Protocol):
    def save_run(self, run: EvalRun) -> None: ...

    def get_run(self, run_id: str) -> EvalRun | None: ...

    def list_runs(self, suite_id: str | None = None) -> list[EvalRun]: ...
