import { useState, useEffect, useMemo } from "react";
import "./App.css";
import { SuiteCard } from "./components/SuiteCard";
import { RunDetail } from "./components/RunDetail";
import { FailuresPanel } from "./components/FailuresPanel";
import { API_BASE_URL } from "./config";

interface Run {
  id: string;
  suite_id: string;
  model: string;
  timestamp: string;
  passed: number;
  total: number;
  system_prompt_name?: string | null;
  revision?: number | null;
  git_commit_hash?: string | null;
}

function App() {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [failuresPanelRunId, setFailuresPanelRunId] = useState<string | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/runs`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch runs");
        return res.json();
      })
      .then((data) => {
        setRuns(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  // Derive suites dynamically from run data, with "basic" first
  const { suites, runsBySuite } = useMemo(() => {
    const grouped: Record<string, Run[]> = {};
    runs.forEach((run) => {
      if (!grouped[run.suite_id]) {
        grouped[run.suite_id] = [];
      }
      grouped[run.suite_id].push(run);
    });
    // Sort with "basic" first, then alphabetically
    const suiteIds = Object.keys(grouped).sort((a, b) => {
      if (a === "basic") return -1;
      if (b === "basic") return 1;
      return a.localeCompare(b);
    });
    return {
      suites: suiteIds.map((id) => ({ id, featured: id === "basic" })),
      runsBySuite: grouped,
    };
  }, [runs]);

  // Fetch suite metadata (title, description, scorer) for each suite
  const [suiteMetadata, setSuiteMetadata] = useState<
    Record<string, { id: string; title?: string; description?: string | null; scorer?: string }>
  >({});

  useEffect(() => {
    const suiteIds = [...new Set(runs.map((r) => r.suite_id))];
    if (suiteIds.length === 0) {
      setSuiteMetadata({});
      return;
    }
    let cancelled = false;
    Promise.all(
      suiteIds.map((id) =>
        fetch(`${API_BASE_URL}/api/suites/${id}`)
          .then((res) =>
            res.ok ? res.json() : { id, title: id, description: null }
          )
          .catch(() => ({ id, title: id, description: null }))
      )
    ).then((results) => {
      if (cancelled) return;
      const meta: Record<
        string,
        { id: string; title?: string; description?: string | null; scorer?: string }
      > = {};
      results.forEach((s) => {
        meta[s.id] = s;
      });
      setSuiteMetadata(meta);
    });
    return () => {
      cancelled = true;
    };
  }, [runs]);

  if (selectedRunId) {
    return (
      <div className="app">
        <RunDetail runId={selectedRunId} onBack={() => setSelectedRunId(null)} />
      </div>
    );
  }

  if (loading) return <div className="app">Loading...</div>;
  if (error)
    return (
      <div className="app">
        <div className="error">Error: {error}</div>
      </div>
    );

  return (
    <div className="app">
      <h1>LLM Eval Dashboard</h1>
      <p className="demo-description">
        A lightweight evaluation framework for testing LLM behavior across prompt versions,
        models, and system configurations. Track regressions, compare runs, and validate
        responses using rule-based checks or LLM-as-judge scoring.
      </p>

      <div className="dashboard-grid">
        {suites.map((suite) => (
          <SuiteCard
            key={suite.id}
            suiteId={suite.id}
            title={suiteMetadata[suite.id]?.title ?? suite.id}
            description={suiteMetadata[suite.id]?.description ?? undefined}
            scorer={suiteMetadata[suite.id]?.scorer}
            runs={runsBySuite[suite.id] || []}
            featured={suite.featured}
            onShowFailures={setFailuresPanelRunId}
          />
        ))}
      </div>

      {failuresPanelRunId && (
        <FailuresPanel
          runId={failuresPanelRunId}
          onClose={() => setFailuresPanelRunId(null)}
        />
      )}
    </div>
  );
}

export default App;
