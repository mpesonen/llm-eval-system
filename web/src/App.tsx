import { useState, useEffect, useMemo } from "react";
import "./App.css";
import { SuiteCard } from "./components/SuiteCard";
import { RunDetail } from "./components/RunDetail";

interface Run {
  id: string;
  suite_id: string;
  model: string;
  timestamp: string;
  passed: number;
  total: number;
  system_prompt_name?: string | null;
  system_prompt_version?: string | null;
}

function App() {
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/runs")
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

  // Derive suites dynamically from run data
  const { suites, runsBySuite } = useMemo(() => {
    const grouped: Record<string, Run[]> = {};
    runs.forEach((run) => {
      if (!grouped[run.suite_id]) {
        grouped[run.suite_id] = [];
      }
      grouped[run.suite_id].push(run);
    });
    const suiteIds = Object.keys(grouped).sort();
    return {
      suites: suiteIds.map((id) => ({ id, name: id })),
      runsBySuite: grouped,
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

      <div className="dashboard-grid">
        {suites.map((suite) => (
          <SuiteCard
            key={suite.id}
            suiteId={suite.id}
            suiteName={suite.name}
            runs={runsBySuite[suite.id] || []}
          />
        ))}
      </div>
    </div>
  );
}

export default App;
