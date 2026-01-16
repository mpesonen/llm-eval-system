from dotenv import load_dotenv
from langsmith import traceable, wrappers
from openai import OpenAI

load_dotenv()

client = wrappers.wrap_openai(OpenAI())


@traceable
def generate(prompt: str, model: str = "gpt-4o-mini") -> dict:
    """
    Run a single eval-style generation.

    Returns a dict with the prompt, response, and metadata for evaluation.
    """
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    response = completion.choices[0].message.content

    return {
        "prompt": prompt,
        "response": response,
        "model": model,
        "usage": {
            "prompt_tokens": completion.usage.prompt_tokens,
            "completion_tokens": completion.usage.completion_tokens,
            "total_tokens": completion.usage.total_tokens,
        },
        "finish_reason": completion.choices[0].finish_reason,
    }


def main():
    result = generate("What is 2 + 2? Answer with just the number.")

    print(f"Prompt: {result['prompt']}")
    print(f"Response: {result['response']}")
    print(f"Model: {result['model']}")
    print(f"Tokens: {result['usage']['total_tokens']}")


if __name__ == "__main__":
    main()
