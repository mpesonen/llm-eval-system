from datetime import datetime, timezone

import pytest

from src.store.base import EvalResult, EvalRun


def make_result(case_id: str, passed: bool, score: float = None) -> EvalResult:
    if score is None:
        score = 1.0 if passed else 0.0
    return EvalResult(
        id=f"result-{case_id}",
        suite_id="test-suite",
        case_id=case_id,
        model="test-model",
        prompt="test prompt",
        response="test response",
        passed=passed,
        score=score,
        reasons=[] if passed else ["failed"],
        timestamp=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    )


def make_run(run_id: str, results: list[EvalResult], suite_id: str = "test-suite") -> EvalRun:
    return EvalRun(
        id=run_id,
        suite_id=suite_id,
        model="test-model",
        timestamp=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        results=results,
    )


class TestCompareRunsBasic:
    def test_identical_runs_no_regressions(self):
        from src.runner.compare import compare_runs

        baseline = make_run("run-1", [make_result("case-1", passed=True)])
        current = make_run("run-2", [make_result("case-1", passed=True)])

        comparison = compare_runs(baseline, current)

        assert comparison.regressions == 0
        assert comparison.improvements == 0
        assert comparison.unchanged == 1

    def test_pass_to_fail_is_regression(self):
        from src.runner.compare import compare_runs

        baseline = make_run("run-1", [make_result("case-1", passed=True)])
        current = make_run("run-2", [make_result("case-1", passed=False)])

        comparison = compare_runs(baseline, current)

        assert comparison.regressions == 1
        assert comparison.cases[0].regression is True
        assert comparison.cases[0].improvement is False

    def test_fail_to_pass_is_improvement(self):
        from src.runner.compare import compare_runs

        baseline = make_run("run-1", [make_result("case-1", passed=False)])
        current = make_run("run-2", [make_result("case-1", passed=True)])

        comparison = compare_runs(baseline, current)

        assert comparison.improvements == 1
        assert comparison.cases[0].improvement is True
        assert comparison.cases[0].regression is False


class TestCompareRunsScoreThreshold:
    def test_score_decrease_above_threshold_is_regression(self):
        from src.runner.compare import compare_runs

        baseline = make_run("run-1", [make_result("case-1", passed=True, score=0.9)])
        current = make_run("run-2", [make_result("case-1", passed=True, score=0.7)])

        comparison = compare_runs(baseline, current, score_threshold=0.1)

        assert comparison.regressions == 1
        assert comparison.cases[0].regression is True

    def test_score_decrease_below_threshold_is_unchanged(self):
        from src.runner.compare import compare_runs

        baseline = make_run("run-1", [make_result("case-1", passed=True, score=0.9)])
        current = make_run("run-2", [make_result("case-1", passed=True, score=0.85)])

        comparison = compare_runs(baseline, current, score_threshold=0.1)

        assert comparison.regressions == 0
        assert comparison.unchanged == 1

    def test_score_increase_above_threshold_is_improvement(self):
        from src.runner.compare import compare_runs

        baseline = make_run("run-1", [make_result("case-1", passed=True, score=0.7)])
        current = make_run("run-2", [make_result("case-1", passed=True, score=0.9)])

        comparison = compare_runs(baseline, current, score_threshold=0.1)

        assert comparison.improvements == 1
        assert comparison.cases[0].improvement is True


class TestCompareRunsMultipleCases:
    def test_multiple_cases_mixed_results(self):
        from src.runner.compare import compare_runs

        baseline = make_run(
            "run-1",
            [
                make_result("case-1", passed=True),
                make_result("case-2", passed=False),
                make_result("case-3", passed=True),
            ],
        )
        current = make_run(
            "run-2",
            [
                make_result("case-1", passed=False),  # regression
                make_result("case-2", passed=True),  # improvement
                make_result("case-3", passed=True),  # unchanged
            ],
        )

        comparison = compare_runs(baseline, current)

        assert comparison.regressions == 1
        assert comparison.improvements == 1
        assert comparison.unchanged == 1
        assert len(comparison.cases) == 3


class TestCompareRunsEdgeCases:
    def test_missing_case_in_current_handled(self):
        from src.runner.compare import compare_runs

        baseline = make_run(
            "run-1",
            [make_result("case-1", passed=True), make_result("case-2", passed=True)],
        )
        current = make_run("run-2", [make_result("case-1", passed=True)])

        comparison = compare_runs(baseline, current)

        # case-2 missing in current should be flagged
        assert len(comparison.cases) == 2

    def test_new_case_in_current_handled(self):
        from src.runner.compare import compare_runs

        baseline = make_run("run-1", [make_result("case-1", passed=True)])
        current = make_run(
            "run-2",
            [make_result("case-1", passed=True), make_result("case-2", passed=True)],
        )

        comparison = compare_runs(baseline, current)

        # case-2 is new, should be included
        assert len(comparison.cases) == 2

    def test_different_suite_ids_raises_error(self):
        from src.runner.compare import compare_runs

        baseline = make_run("run-1", [], suite_id="suite-a")
        current = make_run("run-2", [], suite_id="suite-b")

        with pytest.raises(ValueError, match="suite"):
            compare_runs(baseline, current)

    def test_comparison_includes_run_ids(self):
        from src.runner.compare import compare_runs

        baseline = make_run("baseline-run", [make_result("case-1", passed=True)])
        current = make_run("current-run", [make_result("case-1", passed=True)])

        comparison = compare_runs(baseline, current)

        assert comparison.baseline_run_id == "baseline-run"
        assert comparison.current_run_id == "current-run"
