import json

from src.scorers.base import ScoreResult


class RuleScorer:
    def score(self, prompt: str, response: str, expected: dict) -> ScoreResult:
        reasons: list[str] = []

        if "contains" in expected:
            if expected["contains"] not in response:
                reasons.append(f"Contains: expected '{expected['contains']}' not found")

        if "contains_any" in expected:
            if not any(s in response for s in expected["contains_any"]):
                reasons.append(
                    f"Contains_any: none of {expected['contains_any']} found"
                )

        if "max_length" in expected:
            if len(response) > expected["max_length"]:
                reasons.append(
                    f"Length: {len(response)} exceeds max {expected['max_length']}"
                )

        if "min_length" in expected:
            if len(response) < expected["min_length"]:
                reasons.append(
                    f"Length: {len(response)} below min {expected['min_length']}"
                )

        # Word count rules
        word_count = len(response.split())

        if "max_words" in expected:
            if word_count > expected["max_words"]:
                reasons.append(
                    f"Word count: {word_count} exceeds max {expected['max_words']}"
                )

        if "min_words" in expected:
            if word_count < expected["min_words"]:
                reasons.append(
                    f"Word count: {word_count} below min {expected['min_words']}"
                )

        if "exact_words" in expected:
            if word_count != expected["exact_words"]:
                reasons.append(
                    f"Word count: {word_count} != expected {expected['exact_words']}"
                )

        if "valid_json" in expected and expected["valid_json"]:
            try:
                json.loads(response)
            except json.JSONDecodeError:
                reasons.append("JSON: invalid JSON")

        if "json_has_keys" in expected:
            try:
                data = json.loads(response)
                missing = [k for k in expected["json_has_keys"] if k not in data]
                if missing:
                    reasons.append(f"JSON keys: missing {missing}")
            except json.JSONDecodeError:
                reasons.append("JSON keys: cannot parse JSON")

        passed = len(reasons) == 0
        score = 1.0 if passed else 0.0

        return ScoreResult(passed=passed, score=score, reasons=reasons)
