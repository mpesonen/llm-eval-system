import argparse

from dotenv import load_dotenv

from src.clients.openai import OpenAIClient
from src.runner.loader import load_suite
from src.runner.runner import Runner
from src.scorers.rules import RuleScorer
from src.store.local import LocalStore

load_dotenv()


def print_run(run):
    print(f"Suite: {run.suite_id}")
    print(f"Model: {run.model}")
    print(f"Results: {len(run.results)} case(s)")
    print()

    for result in run.results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.case_id}")
        print(f"  Prompt: {result.prompt}")
        print(f"  Response: {result.response}")
        if result.reasons:
            print(f"  Reasons: {result.reasons}")


def main():
    parser = argparse.ArgumentParser(description="Run LLM evaluation suites")
    parser.add_argument(
        "-s", "--suite", required=True, help="Path to YAML suite file"
    )
    parser.add_argument(
        "-m",
        "--model",
        action="append",
        default=[],
        help="Model to evaluate (can be repeated)",
    )
    args = parser.parse_args()

    models = args.model if args.model else ["gpt-4o-mini"]
    suite = load_suite(args.suite)
    scorer = RuleScorer()
    store = LocalStore()

    for model in models:
        client = OpenAIClient(model=model)
        runner = Runner(client=client, scorer=scorer)
        run = runner.run(suite)
        store.save_run(run)
        print_run(run)
        print("-" * 40)


if __name__ == "__main__":
    main()
