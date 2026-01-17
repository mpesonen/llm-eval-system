from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.prompts import list_prompts
from src.runner.compare import compare_runs
from src.runner.loader import load_suite
from src.store.local import LocalStore

app = FastAPI(title="LLM Eval API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = LocalStore()


@app.get("/api/runs")
def list_runs():
    runs = store.list_runs()
    return [
        {
            "id": run.id,
            "suite_id": run.suite_id,
            "model": run.model,
            "timestamp": run.timestamp.isoformat(),
            "passed": sum(1 for r in run.results if r.passed),
            "total": len(run.results),
            "system_prompt_name": run.system_prompt_name,
            "revision": run.revision,
            "git_commit_hash": run.git_commit_hash,
        }
        for run in runs
    ]


@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    return {
        "id": run.id,
        "suite_id": run.suite_id,
        "model": run.model,
        "timestamp": run.timestamp.isoformat(),
        "system_prompt_name": run.system_prompt_name,
        "revision": run.revision,
        "git_commit_hash": run.git_commit_hash,
        "results": [
            {
                "id": r.id,
                "case_id": r.case_id,
                "prompt": r.prompt,
                "response": r.response,
                "passed": r.passed,
                "score": r.score,
                "reasons": r.reasons,
                "system_prompt_name": r.system_prompt_name,
            }
            for r in run.results
        ],
    }


@app.get("/api/compare")
def compare(baseline: str, current: str):
    baseline_run = store.get_run(baseline)
    current_run = store.get_run(current)

    if not baseline_run:
        raise HTTPException(status_code=404, detail=f"Baseline run '{baseline}' not found")
    if not current_run:
        raise HTTPException(status_code=404, detail=f"Current run '{current}' not found")

    try:
        comparison = compare_runs(baseline_run, current_run)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "baseline_run_id": comparison.baseline_run_id,
        "current_run_id": comparison.current_run_id,
        "regressions": comparison.regressions,
        "improvements": comparison.improvements,
        "unchanged": comparison.unchanged,
        "cases": [
            {
                "case_id": c.case_id,
                "baseline_passed": c.baseline_passed,
                "current_passed": c.current_passed,
                "baseline_score": c.baseline_score,
                "current_score": c.current_score,
                "regression": c.regression,
                "improvement": c.improvement,
            }
            for c in comparison.cases
        ],
    }


@app.get("/api/system-prompts")
def get_system_prompts():
    """List all available system prompts."""
    return list_prompts()


def _get_suites_dir() -> Path:
    """Get the datasets/examples directory path."""
    return Path(__file__).resolve().parent.parent.parent / "datasets" / "examples"


@app.get("/api/suites/{suite_id}")
def get_suite(suite_id: str):
    """Return suite metadata including test cases from the suite YAML file."""
    if ".." in suite_id or "/" in suite_id or "\\" in suite_id:
        raise HTTPException(status_code=400, detail="Invalid suite_id")
    suites_dir = _get_suites_dir()
    suite_path = suites_dir / f"{suite_id}.yaml"
    if not suite_path.exists():
        raise HTTPException(status_code=404, detail="Suite not found")
    try:
        suite = load_suite(str(suite_path))
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load suite")
    return {
        "id": suite.get("id", suite_id),
        "title": suite.get("title") or suite.get("id", suite_id),
        "description": suite.get("description"),
        "scorer": suite.get("scorer", "rules"),
        "llm_criteria": suite.get("llm_criteria"),
        "cases": [
            {
                "id": case["id"],
                "prompt": case["prompt"],
                "expected": case.get("expected", {}),
            }
            for case in suite.get("cases", [])
        ],
    }
