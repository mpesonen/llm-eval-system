# Comparative LLM Eval Runner & Visualizer

## Purpose

A lightweight system to **run, compare, and visualize evaluation suites for Large Language Models (LLMs)**.

Focus areas:
- regression detection
- instruction & safety adherence
- structured output reliability
- model and prompt comparison over time

This is **not a benchmark or leaderboard**.  
It is a **CI-style quality gate for LLM systems**.

---

## Core Requirements

- Same eval suite runs unchanged across different models
- Model and provider details fully abstracted
- Deterministic-ish evaluation with variance tracking
- Clear visualization of regressions
- Easy to extend and reason about

---

## Architecture (Logical)

```text
eval_datasets/
      ↓
eval_runner
      ↓
model_clients (abstracted)
      ↓
scorers / validators
      ↓
results_store
      ↓
visualizer (React)
```

Each layer is intentionally decoupled.

---

## Evaluation Suites

An **evaluation suite** is a versioned set of test cases describing *expected behavior*.

Each test case defines:
- prompt (and optional context)
- evaluation criteria
- metadata (category, severity, tags)

Example categories:
- instruction following
- safety / refusal behavior
- structured output validity
- hallucination resistance
- regression comparison

---

## Model Abstraction

All models are accessed through a provider-agnostic interface.

```ts
interface ModelClient {
  generate(request: ModelRequest): Promise<ModelResponse>
}
```

Concrete implementations:

- AWS Bedrock (Claude, Titan, etc.)
- OpenAI (optional)
- Mock / replay client (testing)

Eval definitions must not reference provider or model names directly.

Model configuration is externalized and versioned.

---

## Evaluation & Scoring

Each test produces:

- pass / fail
- numeric score (0–1)
- failure reasons
- raw model output

Scoring strategies may include:

- rule-based checks (schema, length, keywords)
- heuristic scoring (clarity, uncertainty)
- LLM-as-judge (strict, constrained prompts)
- baseline comparison (semantic delta)

Multiple runs per test are supported to detect instability.

---

## Regression Detection

Evaluation runs can be compared against:

- previous runs
- known-good baselines
- different models

Regressions are flagged when:

- pass → fail transitions occur
- score deltas exceed thresholds
- output variance increases

---

## Observability & Tracing (LangSmith)

LangSmith is used for:

- prompt and model tracing
- run-level metadata
- experiment comparison
- debugging evaluation failures

LangSmith is treated as optional infrastructure:

- eval logic does not depend on it
- system remains functional without it
- tracing can be enabled or disabled via configuration

---

## Frontend (React)

A minimal visualizer focused on clarity:

- list of evaluation runs
- pass/fail summaries
- metric trends
- regression highlights
- drill-down into failed cases

UI prioritizes inspection over interaction.

---

## AWS Alignment

Typical deployment mapping:

- Models: AWS Bedrock
- Storage: S3 (datasets and results)
- Metadata: DynamoDB
- Backend: Lambda or ECS (eval runner)
- Frontend: S3 + CloudFront
- Monitoring: CloudWatch

Cloud services are implementation details, not hard dependencies.

---

## Non-Goals

- Model ranking or public leaderboards
- Objective "ground truth" scoring
- Full MLOps platform
- Autonomous optimization loops

---

## Intended Use

- Validate prompt or model changes
- Detect safety or behavior regressions
- CI integration for LLM-based systems
- Internal quality dashboards

---

## Status

Demo / exploration project focused on:

- LLMOps evaluation patterns
- production-oriented system design
- clarity over completeness

## License
MIT
