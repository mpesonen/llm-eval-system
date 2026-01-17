"""LLM-as-judge scorer using GPT-4.1."""

import json

from src.clients.openai import OpenAIClient
from src.clients.base import ModelRequest
from src.scorers.base import ScoreResult


JUDGE_SYSTEM_PROMPT = """You are an evaluation judge. Your task is to assess whether an AI assistant's response meets the specified criteria.

You will be given:
1. The original prompt sent to the assistant
2. The assistant's response
3. Evaluation criteria

Evaluate the response against the criteria and return a JSON object with:
- "passed": boolean (true if the response meets the criteria, false otherwise)
- "reasoning": string (brief explanation of your judgment)

Return ONLY the JSON object, no other text."""


JUDGE_PROMPT_TEMPLATE = """## Original Prompt
{prompt}

## Assistant's Response
{response}

## Evaluation Criteria
{criteria}

Evaluate the response and return your judgment as JSON."""


class LLMScorer:
    """Scorer that uses an LLM as judge to evaluate responses."""

    def __init__(self, model: str = "gpt-4.1"):
        self.client = OpenAIClient(model=model)

    def score(self, prompt: str, response: str, expected: dict) -> ScoreResult:
        """
        Score a response using LLM-as-judge.
        
        Args:
            prompt: The original prompt sent to the model
            response: The model's response
            expected: Dict containing 'llm_criteria' key with evaluation criteria
            
        Returns:
            ScoreResult with pass/fail and reasoning
        """
        criteria = expected.get("llm_criteria", "")
        if not criteria:
            return ScoreResult(
                passed=False,
                score=0.0,
                reasons=["No llm_criteria provided for LLM scoring"],
            )

        judge_prompt = JUDGE_PROMPT_TEMPLATE.format(
            prompt=prompt,
            response=response,
            criteria=criteria,
        )

        judge_response = self.client.generate(
            ModelRequest(
                prompt=judge_prompt,
                system_prompt=JUDGE_SYSTEM_PROMPT,
            )
        )

        # Parse the JSON response
        try:
            result = json.loads(judge_response.content)
            passed = result.get("passed", False)
            reasoning = result.get("reasoning", "No reasoning provided")
            
            return ScoreResult(
                passed=passed,
                score=1.0 if passed else 0.0,
                reasons=[reasoning],
            )
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract meaning from response
            content_lower = judge_response.content.lower()
            passed = "true" in content_lower and "passed" in content_lower
            
            return ScoreResult(
                passed=passed,
                score=1.0 if passed else 0.0,
                reasons=[f"Judge response (unparsed): {judge_response.content[:200]}"],
            )
