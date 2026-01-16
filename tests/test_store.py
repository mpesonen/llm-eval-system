from datetime import datetime, timezone

import pytest

from src.store.base import EvalResult, EvalRun


def make_result(
    id: str = "result-1",
    suite_id: str = "suite-1",
    case_id: str = "case-1",
    passed: bool = True,
) -> EvalResult:
    return EvalResult(
        id=id,
        suite_id=suite_id,
        case_id=case_id,
        model="test-model",
        prompt="test prompt",
        response="test response",
        passed=passed,
        score=1.0 if passed else 0.0,
        reasons=[] if passed else ["failed"],
        timestamp=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    )


def make_run(
    id: str = "run-1",
    suite_id: str = "suite-1",
    results: list[EvalResult] | None = None,
    timestamp: datetime | None = None,
) -> EvalRun:
    return EvalRun(
        id=id,
        suite_id=suite_id,
        model="test-model",
        timestamp=timestamp or datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        results=results if results is not None else [make_result()],
    )


class TestLocalStoreSaveAndGet:
    def test_saves_and_retrieves_run(self, tmp_path):
        from src.store.local import LocalStore

        store = LocalStore(path=str(tmp_path))
        run = make_run(id="run-123")

        store.save_run(run)
        retrieved = store.get_run("run-123")

        assert retrieved is not None
        assert retrieved.id == "run-123"
        assert retrieved.suite_id == "suite-1"

    def test_returns_none_for_nonexistent_run(self, tmp_path):
        from src.store.local import LocalStore

        store = LocalStore(path=str(tmp_path))

        assert store.get_run("nonexistent") is None

    def test_persists_datetime_correctly(self, tmp_path):
        from src.store.local import LocalStore

        store = LocalStore(path=str(tmp_path))
        timestamp = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        run = make_run(id="run-dt", timestamp=timestamp)

        store.save_run(run)
        retrieved = store.get_run("run-dt")

        assert retrieved.timestamp == timestamp

    def test_persists_nested_results(self, tmp_path):
        from src.store.local import LocalStore

        store = LocalStore(path=str(tmp_path))
        results = [
            make_result(id="r1", case_id="case-1", passed=True),
            make_result(id="r2", case_id="case-2", passed=False),
        ]
        run = make_run(id="run-nested", results=results)

        store.save_run(run)
        retrieved = store.get_run("run-nested")

        assert len(retrieved.results) == 2
        assert retrieved.results[0].case_id == "case-1"
        assert retrieved.results[0].passed is True
        assert retrieved.results[1].case_id == "case-2"
        assert retrieved.results[1].passed is False

    def test_handles_empty_results(self, tmp_path):
        from src.store.local import LocalStore

        store = LocalStore(path=str(tmp_path))
        run = make_run(id="run-empty", results=[])

        store.save_run(run)
        retrieved = store.get_run("run-empty")

        assert retrieved.results == []


class TestLocalStoreListRuns:
    def test_returns_empty_list_when_no_runs(self, tmp_path):
        from src.store.local import LocalStore

        store = LocalStore(path=str(tmp_path))

        assert store.list_runs() == []

    def test_returns_all_runs_when_no_filter(self, tmp_path):
        from src.store.local import LocalStore

        store = LocalStore(path=str(tmp_path))
        store.save_run(make_run(id="run-1", suite_id="suite-a"))
        store.save_run(make_run(id="run-2", suite_id="suite-b"))

        runs = store.list_runs()

        assert len(runs) == 2
        run_ids = {r.id for r in runs}
        assert run_ids == {"run-1", "run-2"}

    def test_filters_by_suite_id(self, tmp_path):
        from src.store.local import LocalStore

        store = LocalStore(path=str(tmp_path))
        store.save_run(make_run(id="run-1", suite_id="suite-a"))
        store.save_run(make_run(id="run-2", suite_id="suite-b"))
        store.save_run(make_run(id="run-3", suite_id="suite-a"))

        runs = store.list_runs(suite_id="suite-a")

        assert len(runs) == 2
        assert all(r.suite_id == "suite-a" for r in runs)

    def test_returns_newest_first(self, tmp_path):
        from src.store.local import LocalStore

        store = LocalStore(path=str(tmp_path))
        store.save_run(
            make_run(
                id="old",
                timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            )
        )
        store.save_run(
            make_run(
                id="new",
                timestamp=datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc),
            )
        )

        runs = store.list_runs()

        assert runs[0].id == "new"
        assert runs[1].id == "old"


class TestLocalStoreEdgeCases:
    def test_creates_directory_if_not_exists(self, tmp_path):
        from src.store.local import LocalStore

        new_path = tmp_path / "nested" / "store"
        store = LocalStore(path=str(new_path))

        store.save_run(make_run(id="run-1"))

        assert new_path.exists()
        assert store.get_run("run-1") is not None
