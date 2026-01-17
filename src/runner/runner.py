import uuid
from datetime import datetime, timezone

from src.clients.base import ModelClient, ModelRequest
from src.prompts import load_prompt, prompt_exists
from src.scorers.base import Scorer
from src.scorers.rules import RuleScorer
from src.scorers.llm import LLMScorer
from src.store.base import EvalResult, EvalRun
from src.utils.git import get_current_commit_hash


def get_scorer_for_suite(suite: dict) -> Scorer:
    """Get the appropriate scorer based on suite configuration."""
    scorer_type = suite.get("scorer", "rules")
    
    if scorer_type == "llm":
        return LLMScorer()
    else:
        return RuleScorer()


class Runner:
    def __init__(self, client: ModelClient, scorer: Scorer | None = None):
        self.client = client
        self._scorer = scorer

    def run(
        self,
        suite: dict,
        system_prompt_name: str | None = None,
    ) -> EvalRun:
        suite_id = suite["id"]
        cases = suite.get("cases", [])
        results: list[EvalResult] = []
        model_name: str | None = None
        
        # Select scorer: use provided scorer or auto-select from suite config
        scorer = self._scorer if self._scorer else get_scorer_for_suite(suite)
        
        # Get suite-level llm_criteria for LLM scoring
        suite_llm_criteria = suite.get("llm_criteria", "")
        
        # Load system prompt if specified
        system_prompt_content: str | None = None
        
        if system_prompt_name:
            if not prompt_exists(system_prompt_name):
                raise ValueError(
                    f"System prompt '{system_prompt_name}' not found"
                )
            system_prompt_content = load_prompt(system_prompt_name)

        for case in cases:
            case_id = case["id"]
            prompt = case["prompt"]
            expected = case.get("expected", {})
            
            # Inject suite-level llm_criteria if not specified at case level
            if suite_llm_criteria and "llm_criteria" not in expected:
                expected = {**expected, "llm_criteria": suite_llm_criteria}

            response = self.client.generate(
                ModelRequest(
                    prompt=prompt,
                    system_prompt=system_prompt_content,
                )
            )
            model_name = response.model

            score_result = scorer.score(prompt, response.content, expected)

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
                )
            )

        return EvalRun(
            id=str(uuid.uuid4()),
            suite_id=suite_id,
            model=model_name or "unknown",
            timestamp=datetime.now(timezone.utc),
            results=results,
            system_prompt_name=system_prompt_name,
            git_commit_hash=get_current_commit_hash(),
        )
