from dotenv import load_dotenv

from src.clients.openai import OpenAIClient
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
    models = ["gpt-4o-mini", "gpt-4o"]
    scorer = RuleScorer()
    store = LocalStore()

    suite = {
        "id": "quick-test",
        "cases": [
            {
                "id": "math",
                "prompt": "What is 2 + 2? Answer with just the number.",
                "expected": {"contains": "4", "max_length": 10},
            },
        ],
    }

    for model in models:
        client = OpenAIClient(model=model)
        runner = Runner(client=client, scorer=scorer)
        run = runner.run(suite)
        store.save_run(run)
        print_run(run)
        print("-" * 40)


if __name__ == "__main__":
    main()
