from dotenv import load_dotenv

from src.clients.openai import OpenAIClient
from src.runner.runner import Runner
from src.scorers.rules import RuleScorer

load_dotenv()


def main():
    client = OpenAIClient()
    scorer = RuleScorer()
    runner = Runner(client=client, scorer=scorer)

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

    run = runner.run(suite)

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


if __name__ == "__main__":
    main()
