import uuid
from datetime import datetime, timezone

from src.clients.base import ModelClient, ModelRequest
from src.scorers.base import Scorer
from src.store.base import EvalResult, EvalRun


class Runner:
    def __init__(self, client: ModelClient, scorer: Scorer):
        self.client = client
        self.scorer = scorer

    def run(self, suite: dict) -> EvalRun:
        suite_id = suite["id"]
        cases = suite.get("cases", [])
        results: list[EvalResult] = []
        model_name: str | None = None

        for case in cases:
            case_id = case["id"]
            prompt = case["prompt"]
            expected = case.get("expected", {})

            response = self.client.generate(ModelRequest(prompt=prompt))
            model_name = response.model

            score_result = self.scorer.score(prompt, response.content, expected)

            results.append(
                EvalResult(
                    id=str(uuid.uuid4()),
                    suite_id=suite_id,
                    case_id=case_id,
                    model=response.model,
                    prompt=prompt,
                    response=response.content,
                    passed=score_result.passed,
                    score=score_result.score,
                    reasons=score_result.reasons,
                    timestamp=datetime.now(timezone.utc),
                )
            )

        return EvalRun(
            id=str(uuid.uuid4()),
            suite_id=suite_id,
            model=model_name or "unknown",
            timestamp=datetime.now(timezone.utc),
            results=results,
        )
