import uuid
from datetime import datetime, timezone

from src.clients.base import ModelClient, ModelRequest
from src.prompts import load_prompt, load_latest_prompt, prompt_exists
from src.scorers.base import Scorer
from src.store.base import EvalResult, EvalRun


class Runner:
    def __init__(self, client: ModelClient, scorer: Scorer):
        self.client = client
        self.scorer = scorer

    def run(
        self,
        suite: dict,
        system_prompt_name: str | None = None,
        system_prompt_version: str | None = None,
    ) -> EvalRun:
        suite_id = suite["id"]
        cases = suite.get("cases", [])
        results: list[EvalResult] = []
        model_name: str | None = None
        
        # Load system prompt if specified
        system_prompt_content: str | None = None
        resolved_version: str | None = None
        
        if system_prompt_name:
            if not prompt_exists(system_prompt_name):
                raise ValueError(
                    f"System prompt '{system_prompt_name}' not found"
                )
            
            if system_prompt_version:
                if not prompt_exists(system_prompt_name, system_prompt_version):
                    raise ValueError(
                        f"System prompt '{system_prompt_name}' version '{system_prompt_version}' not found"
                    )
                system_prompt_content = load_prompt(
                    system_prompt_name, system_prompt_version
                )
                resolved_version = system_prompt_version
            else:
                # Load latest version
                system_prompt_content, resolved_version = load_latest_prompt(
                    system_prompt_name
                )

        for case in cases:
            case_id = case["id"]
            prompt = case["prompt"]
            expected = case.get("expected", {})

            response = self.client.generate(
                ModelRequest(
                    prompt=prompt,
                    system_prompt=system_prompt_content,
                )
            )
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
                    system_prompt_name=system_prompt_name,
                    system_prompt_version=resolved_version,
                )
            )

        return EvalRun(
            id=str(uuid.uuid4()),
            suite_id=suite_id,
            model=model_name or "unknown",
            timestamp=datetime.now(timezone.utc),
            results=results,
            system_prompt_name=system_prompt_name,
            system_prompt_version=resolved_version,
        )
