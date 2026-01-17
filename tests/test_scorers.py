import pytest


class TestRuleScorerContains:
    def test_passes_when_substring_found(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "The answer is 4", {"contains": "4"})

        assert result.passed is True
        assert result.score == 1.0

    def test_fails_when_substring_not_found(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "The answer is 5", {"contains": "4"})

        assert result.passed is False
        assert result.score == 0.0
        assert "contains" in result.reasons[0].lower()

    def test_case_sensitive_by_default(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "Hello World", {"contains": "hello"})

        assert result.passed is False


class TestRuleScorerContainsAny:
    def test_passes_when_any_substring_found(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score(
            "", "I cannot help with that", {"contains_any": ["I can't", "I cannot", "sorry"]}
        )

        assert result.passed is True

    def test_fails_when_no_substring_found(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score(
            "", "Here is how to do it", {"contains_any": ["I can't", "I cannot", "sorry"]}
        )

        assert result.passed is False
        assert "contains_any" in result.reasons[0].lower()


class TestRuleScorerMaxLength:
    def test_passes_when_under_limit(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "4", {"max_length": 10})

        assert result.passed is True

    def test_fails_when_over_limit(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "This is a very long response", {"max_length": 10})

        assert result.passed is False
        assert "length" in result.reasons[0].lower()

    def test_passes_at_exact_limit(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "1234567890", {"max_length": 10})

        assert result.passed is True


class TestRuleScorerMinLength:
    def test_passes_when_over_limit(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "This is long enough", {"min_length": 10})

        assert result.passed is True

    def test_fails_when_under_limit(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "short", {"min_length": 10})

        assert result.passed is False
        assert "length" in result.reasons[0].lower()

    def test_passes_at_exact_limit(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "1234567890", {"min_length": 10})

        assert result.passed is True


class TestRuleScorerWordCount:
    def test_max_words_passes_when_under(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "one two three", {"max_words": 5})

        assert result.passed is True

    def test_max_words_fails_when_over(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "one two three four five six", {"max_words": 5})

        assert result.passed is False
        assert "word count" in result.reasons[0].lower()

    def test_min_words_passes_when_over(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "one two three four five", {"min_words": 3})

        assert result.passed is True

    def test_min_words_fails_when_under(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "one two", {"min_words": 5})

        assert result.passed is False
        assert "word count" in result.reasons[0].lower()

    def test_exact_words_passes_when_exact(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "one two three four five", {"exact_words": 5})

        assert result.passed is True

    def test_exact_words_fails_when_too_few(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "one two three", {"exact_words": 5})

        assert result.passed is False
        assert "word count" in result.reasons[0].lower()

    def test_exact_words_fails_when_too_many(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "one two three four five six seven", {"exact_words": 5})

        assert result.passed is False
        assert "word count" in result.reasons[0].lower()


class TestRuleScorerValidJson:
    def test_passes_for_valid_json(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", '{"name": "Alice", "age": 30}', {"valid_json": True})

        assert result.passed is True

    def test_fails_for_invalid_json(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "not json at all", {"valid_json": True})

        assert result.passed is False
        assert "json" in result.reasons[0].lower()

    def test_fails_for_partial_json(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", '{"name": "Alice"', {"valid_json": True})

        assert result.passed is False


class TestRuleScorerJsonHasKeys:
    def test_passes_when_all_keys_present(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score(
            "", '{"name": "Alice", "age": 30}', {"json_has_keys": ["name", "age"]}
        )

        assert result.passed is True

    def test_fails_when_key_missing(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", '{"name": "Alice"}', {"json_has_keys": ["name", "age"]})

        assert result.passed is False
        assert "age" in result.reasons[0]

    def test_fails_for_invalid_json(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "not json", {"json_has_keys": ["name"]})

        assert result.passed is False


class TestRuleScorerMultipleRules:
    def test_all_rules_must_pass(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "4", {"contains": "4", "max_length": 10})

        assert result.passed is True

    def test_fails_if_any_rule_fails(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "4", {"contains": "4", "max_length": 0})

        assert result.passed is False

    def test_collects_all_failure_reasons(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "wrong", {"contains": "4", "max_length": 2})

        assert result.passed is False
        assert len(result.reasons) == 2

    def test_empty_expected_passes(self):
        from src.scorers.rules import RuleScorer

        scorer = RuleScorer()
        result = scorer.score("", "any response", {})

        assert result.passed is True
        assert result.score == 1.0
