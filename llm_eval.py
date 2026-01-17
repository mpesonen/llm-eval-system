import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.clients import get_client
from src.runner.compare import compare_runs
from src.runner.loader import load_suite
from src.runner.runner import Runner
from src.scorers.rules import RuleScorer
from src.store.local import LocalStore

load_dotenv()


def get_all_suite_paths(suites_dir: Path | None = None) -> list[Path]:
    """Discover all YAML suite files in the given directory."""
    if suites_dir is None:
        suites_dir = Path(__file__).parent / "datasets" / "examples"
    
    if not suites_dir.exists():
        return []
    
    return sorted(suites_dir.glob("*.yaml"))


def print_run(run):
    print(f"Suite: {run.suite_id}")
    print(f"Model: {run.model}")
    if run.system_prompt_name:
        version_str = f" ({run.system_prompt_version})" if run.system_prompt_version else ""
        print(f"System Prompt: {run.system_prompt_name}{version_str}")
    print(f"Results: {len(run.results)} case(s)")
    print()

    for result in run.results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.case_id}")
        print(f"  Prompt: {result.prompt}")
        print(f"  Response: {result.response}")
        if result.reasons:
            print(f"  Reasons: {result.reasons}")


def print_comparison(comparison, baseline, current):
    print("Comparing runs:")
    print(f"  Baseline: {baseline.id[:8]}... ({baseline.model}, {baseline.timestamp.strftime('%Y-%m-%d %H:%M')})")
    print(f"  Current:  {current.id[:8]}... ({current.model}, {current.timestamp.strftime('%Y-%m-%d %H:%M')})")
    print()
    print(f"Regressions: {comparison.regressions} | Improvements: {comparison.improvements} | Unchanged: {comparison.unchanged}")
    print()

    for case in comparison.cases:
        if case.regression:
            label = "REGRESSION"
        elif case.improvement:
            label = "IMPROVEMENT"
        else:
            label = "UNCHANGED"

        baseline_status = "PASS" if case.baseline_passed else "FAIL"
        current_status = "PASS" if case.current_passed else "FAIL"
        baseline_score = f"{case.baseline_score:.1f}" if case.baseline_score is not None else "?"
        current_score = f"{case.current_score:.1f}" if case.current_score is not None else "?"

        print(f"[{label}] {case.case_id}")
        print(f"  {baseline_status} ({baseline_score}) → {current_status} ({current_score})")


def list_runs(store):
    runs = store.list_runs()
    if not runs:
        print("No stored runs found.")
        return

    print(f"Stored runs ({len(runs)}):")
    print()
    for run in runs:
        passed = sum(1 for r in run.results if r.passed)
        total = len(run.results)
        print(f"  {run.id}")
        print(f"    Suite: {run.suite_id} | Model: {run.model}")
        print(f"    Results: {passed}/{total} passed | {run.timestamp.strftime('%Y-%m-%d %H:%M')}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Run LLM evaluation suites")
    parser.add_argument(
        "-s", "--suite", help="Path to YAML suite file"
    )
    parser.add_argument(
        "-a", "--all-suites", action="store_true",
        help="Run all suites in datasets/examples/"
    )
    parser.add_argument(
        "--suites-dir",
        help="Directory containing suite files (used with --all-suites)"
    )
    parser.add_argument(
        "-m",
        "--model",
        action="append",
        default=[],
        help="Model to evaluate (can be repeated)",
    )
    parser.add_argument(
        "-l", "--list", action="store_true", help="List stored runs"
    )
    parser.add_argument(
        "-c", "--compare", nargs=2, metavar=("BASELINE", "CURRENT"),
        help="Compare two runs by ID"
    )
    parser.add_argument(
        "--system-prompt",
        help="System prompt name to use (e.g., 'example')"
    )
    parser.add_argument(
        "--system-prompt-version",
        help="System prompt version (e.g., 'v1'). Defaults to latest if not specified."
    )
    args = parser.parse_args()

    store = LocalStore()

    # List runs
    if args.list:
        list_runs(store)
        return

    # Compare runs
    if args.compare:
        baseline_id, current_id = args.compare
        baseline = store.get_run(baseline_id)
        current = store.get_run(current_id)

        if not baseline:
            print(f"Error: Baseline run '{baseline_id}' not found.", file=sys.stderr)
            sys.exit(1)
        if not current:
            print(f"Error: Current run '{current_id}' not found.", file=sys.stderr)
            sys.exit(1)

        comparison = compare_runs(baseline, current)
        print_comparison(comparison, baseline, current)
        return

    # Determine which suites to run
    if args.all_suites:
        suites_dir = Path(args.suites_dir) if args.suites_dir else None
        suite_paths = get_all_suite_paths(suites_dir)
        if not suite_paths:
            print("No suite files found.", file=sys.stderr)
            sys.exit(1)
        print(f"Found {len(suite_paths)} suite(s) to run:")
        for p in suite_paths:
            print(f"  - {p.name}")
        print()
    elif args.suite:
        suite_paths = [Path(args.suite)]
    else:
        parser.error("--suite or --all-suites is required when running evaluations")

    models = args.model if args.model else ["gpt-4o-mini"]
    scorer = RuleScorer()

    for suite_path in suite_paths:
        suite = load_suite(str(suite_path))
        print(f"=== Suite: {suite.get('id', suite_path.stem)} ===")
        print()

        for model in models:
            client = get_client(model)
            runner = Runner(client=client, scorer=scorer)
            run = runner.run(
                suite,
                system_prompt_name=args.system_prompt,
                system_prompt_version=args.system_prompt_version,
            )
            store.save_run(run)
            print_run(run)
            print("-" * 40)

        print()


if __name__ == "__main__":
    main()
