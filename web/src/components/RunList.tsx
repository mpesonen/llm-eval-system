import { useEffect, useState } from "react";
import { API_BASE_URL } from "../config";

interface Run {
  id: string;
  suite_id: string;
  model: string;
  timestamp: string;
  passed: number;
  total: number;
}

interface RunListProps {
  onSelectRun: (runId: string) => void;
}

export function RunList({ onSelectRun }: RunListProps) {
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

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (runs.length === 0) return <div>No runs found.</div>;

  return (
    <div className="run-list">
      <h2>Eval Runs</h2>
      <table>
        <thead>
          <tr>
            <th>Suite</th>
            <th>Model</th>
            <th>Results</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr
              key={run.id}
              onClick={() => onSelectRun(run.id)}
              className="clickable"
            >
              <td>{run.suite_id}</td>
              <td>{run.model}</td>
              <td>
                <span className={run.passed === run.total ? "pass" : "partial"}>
                  {run.passed}/{run.total}
                </span>
              </td>
              <td>{new Date(run.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
