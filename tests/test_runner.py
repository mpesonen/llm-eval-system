from dataclasses import dataclass

import pytest

from src.clients.base import ModelRequest, ModelResponse
from src.scorers.base import ScoreResult


@dataclass
class MockClient:
    """Mock client that returns predefined responses."""

    responses: dict[str, str]

    def generate(self, request: ModelRequest) -> ModelResponse:
        content = self.responses.get(request.prompt, "default response")
        return ModelResponse(
            content=content,
            model="mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            finish_reason="stop",
        )


@dataclass
class MockScorer:
    """Mock scorer that passes if response contains expected substring."""

    def score(self, prompt: str, response: str, expected: dict) -> ScoreResult:
        if "contains" in expected:
            passed = expected["contains"] in response
            return ScoreResult(
                passed=passed,
                score=1.0 if passed else 0.0,
                reasons=[] if passed else [f"Expected '{expected['contains']}' not found"],
            )
        return ScoreResult(passed=True, score=1.0, reasons=[])


class TestRunner:
    def test_runs_single_case(self):
        from src.runner.runner import Runner

        client = MockClient(responses={"What is 2+2?": "4"})
        scorer = MockScorer()
        runner = Runner(client=client, scorer=scorer)

        suite = {
            "id": "test-suite",
            "cases": [
                {"id": "math", "prompt": "What is 2+2?", "expected": {"contains": "4"}}
            ],
        }

        run = runner.run(suite)

        assert run.suite_id == "test-suite"
        assert len(run.results) == 1
        assert run.results[0].passed is True
        assert run.results[0].case_id == "math"

    def test_runs_multiple_cases(self):
        from src.runner.runner import Runner

        client = MockClient(
            responses={
                "What is 2+2?": "4",
                "What is 3+3?": "6",
            }
        )
        scorer = MockScorer()
        runner = Runner(client=client, scorer=scorer)

        suite = {
            "id": "test-suite",
            "cases": [
                {"id": "case1", "prompt": "What is 2+2?", "expected": {"contains": "4"}},
                {"id": "case2", "prompt": "What is 3+3?", "expected": {"contains": "6"}},
            ],
        }

        run = runner.run(suite)

        assert len(run.results) == 2
        assert all(r.passed for r in run.results)

    def test_captures_failure(self):
        from src.runner.runner import Runner

        client = MockClient(responses={"What is 2+2?": "5"})  # Wrong answer
        scorer = MockScorer()
        runner = Runner(client=client, scorer=scorer)

        suite = {
            "id": "test-suite",
            "cases": [
                {"id": "math", "prompt": "What is 2+2?", "expected": {"contains": "4"}}
            ],
        }

        run = runner.run(suite)

        assert run.results[0].passed is False
        assert run.results[0].score == 0.0
        assert len(run.results[0].reasons) > 0

    def test_stores_response_content(self):
        from src.runner.runner import Runner

        client = MockClient(responses={"Hello": "Hi there!"})
        scorer = MockScorer()
        runner = Runner(client=client, scorer=scorer)

        suite = {
            "id": "test-suite",
            "cases": [{"id": "greeting", "prompt": "Hello", "expected": {}}],
        }

        run = runner.run(suite)

        assert run.results[0].response == "Hi there!"
        assert run.results[0].prompt == "Hello"

    def test_generates_unique_run_id(self):
        from src.runner.runner import Runner

        client = MockClient(responses={})
        scorer = MockScorer()
        runner = Runner(client=client, scorer=scorer)

        suite = {"id": "test-suite", "cases": []}

        run1 = runner.run(suite)
        run2 = runner.run(suite)

        assert run1.id != run2.id

    def test_records_model_name(self):
        from src.runner.runner import Runner

        client = MockClient(responses={"test": "response"})
        scorer = MockScorer()
        runner = Runner(client=client, scorer=scorer)

        suite = {
            "id": "test-suite",
            "cases": [{"id": "case1", "prompt": "test", "expected": {}}],
        }

        run = runner.run(suite)

        assert run.model == "mock-model"
        assert run.results[0].model == "mock-model"
