from dataclasses import dataclass

from src.store.base import EvalRun


@dataclass
class CaseComparison:
    case_id: str
    baseline_passed: bool | None
    current_passed: bool | None
    baseline_score: float | None
    current_score: float | None
    regression: bool
    improvement: bool


@dataclass
class RunComparison:
    baseline_run_id: str
    current_run_id: str
    cases: list[CaseComparison]
    regressions: int
    improvements: int
    unchanged: int


def compare_runs(
    baseline: EvalRun, current: EvalRun, score_threshold: float = 0.1
) -> RunComparison:
    """Compare two runs and identify regressions and improvements."""
    if baseline.suite_id != current.suite_id:
        raise ValueError(
            f"Cannot compare runs from different suites: {baseline.suite_id} vs {current.suite_id}"
        )

    baseline_results = {r.case_id: r for r in baseline.results}
    current_results = {r.case_id: r for r in current.results}

    all_case_ids = set(baseline_results.keys()) | set(current_results.keys())

    cases: list[CaseComparison] = []
    regressions = 0
    improvements = 0
    unchanged = 0

    for case_id in sorted(all_case_ids):
        baseline_result = baseline_results.get(case_id)
        current_result = current_results.get(case_id)

        baseline_passed = baseline_result.passed if baseline_result else None
        current_passed = current_result.passed if current_result else None
        baseline_score = baseline_result.score if baseline_result else None
        current_score = current_result.score if current_result else None

        regression = False
        improvement = False

        if baseline_passed is not None and current_passed is not None:
            # Check pass/fail transitions
            if baseline_passed and not current_passed:
                regression = True
            elif not baseline_passed and current_passed:
                improvement = True
            # Check score threshold if both passed
            elif baseline_score is not None and current_score is not None:
                score_delta = current_score - baseline_score
                if score_delta < -score_threshold:
                    regression = True
                elif score_delta > score_threshold:
                    improvement = True

        if regression:
            regressions += 1
        elif improvement:
            improvements += 1
        else:
            unchanged += 1

        cases.append(
            CaseComparison(
                case_id=case_id,
                baseline_passed=baseline_passed,
                current_passed=current_passed,
                baseline_score=baseline_score,
                current_score=current_score,
                regression=regression,
                improvement=improvement,
            )
        )

    return RunComparison(
        baseline_run_id=baseline.id,
        current_run_id=current.id,
        cases=cases,
        regressions=regressions,
        improvements=improvements,
        unchanged=unchanged,
    )
