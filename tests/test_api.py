from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

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


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create test client with isolated store."""
    from src.store.local import LocalStore

    test_store = LocalStore(path=str(tmp_path))

    import src.api.server as server_module

    monkeypatch.setattr(server_module, "store", test_store)

    from src.api.server import app

    return TestClient(app), test_store


class TestListRuns:
    def test_returns_empty_list_when_no_runs(self, client):
        test_client, _ = client
        response = test_client.get("/api/runs")

        assert response.status_code == 200
        assert response.json() == []

    def test_returns_runs_with_pass_counts(self, client):
        test_client, store = client
        results = [
            make_result(id="r1", case_id="c1", passed=True),
            make_result(id="r2", case_id="c2", passed=False),
        ]
        store.save_run(make_run(id="run-1", results=results))

        response = test_client.get("/api/runs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "run-1"
        assert data[0]["passed"] == 1
        assert data[0]["total"] == 2

    def test_serializes_timestamp_as_iso(self, client):
        test_client, store = client
        store.save_run(
            make_run(
                id="run-1",
                timestamp=datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc),
            )
        )

        response = test_client.get("/api/runs")

        data = response.json()
        assert data[0]["timestamp"] == "2024-06-15T14:30:00+00:00"


class TestGetRun:
    def test_returns_run_with_results(self, client):
        test_client, store = client
        results = [make_result(id="r1", case_id="c1", passed=True)]
        store.save_run(make_run(id="run-123", results=results))

        response = test_client.get("/api/runs/run-123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "run-123"
        assert len(data["results"]) == 1
        assert data["results"][0]["case_id"] == "c1"
        assert data["results"][0]["passed"] is True

    def test_returns_404_for_nonexistent_run(self, client):
        test_client, _ = client

        response = test_client.get("/api/runs/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestCompare:
    def test_returns_comparison_results(self, client):
        test_client, store = client
        store.save_run(
            make_run(
                id="baseline",
                results=[make_result(id="r1", case_id="c1", passed=True)],
            )
        )
        store.save_run(
            make_run(
                id="current",
                results=[make_result(id="r2", case_id="c1", passed=False)],
            )
        )

        response = test_client.get("/api/compare?baseline=baseline&current=current")

        assert response.status_code == 200
        data = response.json()
        assert data["regressions"] == 1
        assert data["improvements"] == 0
        assert len(data["cases"]) == 1
        assert data["cases"][0]["regression"] is True

    def test_returns_404_for_missing_baseline(self, client):
        test_client, store = client
        store.save_run(make_run(id="current"))

        response = test_client.get("/api/compare?baseline=missing&current=current")

        assert response.status_code == 404
        assert "baseline" in response.json()["detail"].lower()

    def test_returns_404_for_missing_current(self, client):
        test_client, store = client
        store.save_run(make_run(id="baseline"))

        response = test_client.get("/api/compare?baseline=baseline&current=missing")

        assert response.status_code == 404
        assert "current" in response.json()["detail"].lower()


class TestGetSuite:
    def test_returns_suite_metadata_when_suite_exists(self, client):
        test_client, _ = client
        response = test_client.get("/api/suites/basic")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "basic"
        assert data["title"] == "basic"  # fallback when title not in YAML
        assert "Quick-start" in (data["description"] or "")

    def test_returns_title_from_yaml_when_present(self, client):
        test_client, _ = client
        response = test_client.get("/api/suites/structured-output")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "structured-output"
        assert data["title"] == "Structured Output"
        assert "JSON" in (data["description"] or "")

    def test_returns_404_for_nonexistent_suite(self, client):
        test_client, _ = client
        response = test_client.get("/api/suites/nonexistent-suite-xyz")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_returns_400_for_invalid_suite_id(self, client):
        test_client, _ = client
        response = test_client.get("/api/suites/..%2F..%2Fetc")  # ".." and "/" in path

        # FastAPI may return 404 for invalid path; 400 if our check runs
        assert response.status_code in (400, 404)
