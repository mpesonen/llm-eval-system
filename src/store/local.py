import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from src.store.base import EvalResult, EvalRun


class LocalStore:
    def __init__(self, path: str = ".eval_runs"):
        self.path = Path(path)

    def _get_next_revision(self) -> int:
        """Get the next global revision number."""
        runs = self.list_runs()
        if not runs:
            return 1
        # Find the max revision among all runs
        max_revision = 0
        for run in runs:
            if run.revision is not None and run.revision > max_revision:
                max_revision = run.revision
        return max_revision + 1

    def save_run(self, run: EvalRun) -> None:
        self.path.mkdir(parents=True, exist_ok=True)

        # Assign revision number if not already set
        if run.revision is None:
            run.revision = self._get_next_revision()

        data = asdict(run)
        data["timestamp"] = run.timestamp.isoformat()
        for result in data["results"]:
            result["timestamp"] = result["timestamp"].isoformat()

        file_path = self.path / f"{run.id}.json"
        file_path.write_text(json.dumps(data, indent=2))

    def get_run(self, run_id: str) -> EvalRun | None:
        file_path = self.path / f"{run_id}.json"

        if not file_path.exists():
            return None

        data = json.loads(file_path.read_text())
        return self._dict_to_run(data)

    def list_runs(self, suite_id: str | None = None) -> list[EvalRun]:
        if not self.path.exists():
            return []

        runs = []
        for file_path in self.path.glob("*.json"):
            data = json.loads(file_path.read_text())
            run = self._dict_to_run(data)

            if suite_id is None or run.suite_id == suite_id:
                runs.append(run)

        runs.sort(key=lambda r: r.timestamp, reverse=True)
        return runs

    def _dict_to_run(self, data: dict) -> EvalRun:
        results = [
            EvalResult(
                id=r["id"],
                suite_id=r["suite_id"],
                case_id=r["case_id"],
                model=r["model"],
                prompt=r["prompt"],
                response=r["response"],
                passed=r["passed"],
                score=r["score"],
                reasons=r["reasons"],
                timestamp=datetime.fromisoformat(r["timestamp"]),
                system_prompt_name=r.get("system_prompt_name"),
                system_prompt_version=r.get("system_prompt_version"),
            )
            for r in data["results"]
        ]

        return EvalRun(
            id=data["id"],
            suite_id=data["suite_id"],
            model=data["model"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            results=results,
            system_prompt_name=data.get("system_prompt_name"),
            system_prompt_version=data.get("system_prompt_version"),
            revision=data.get("revision"),
            git_commit_hash=data.get("git_commit_hash"),
        )
