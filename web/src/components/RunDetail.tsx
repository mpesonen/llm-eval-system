import { useEffect, useState } from "react";
import { API_BASE_URL } from "../config";

interface Result {
  id: string;
  case_id: string;
  prompt: string;
  response: string;
  passed: boolean;
  score: number;
  reasons: string[];
}

interface RunData {
  id: string;
  suite_id: string;
  model: string;
  timestamp: string;
  results: Result[];
}

interface RunDetailProps {
  runId: string;
  onBack: () => void;
}

export function RunDetail({ runId, onBack }: RunDetailProps) {
  const [run, setRun] = useState<RunData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/runs/${runId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch run");
        return res.json();
      })
      .then((data) => {
        setRun(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [runId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!run) return <div>Run not found.</div>;

  const passed = run.results.filter((r) => r.passed).length;

  return (
    <div className="run-detail">
      <button onClick={onBack} className="back-button">
        &larr; Back to list
      </button>

      <h2>Run Details</h2>

      <div className="run-meta">
        <p>
          <strong>Suite:</strong> {run.suite_id}
        </p>
        <p>
          <strong>Model:</strong> {run.model}
        </p>
        <p>
          <strong>Results:</strong> {passed}/{run.results.length} passed
        </p>
        <p>
          <strong>Timestamp:</strong> {new Date(run.timestamp).toLocaleString()}
        </p>
      </div>

      <h3>Results</h3>
      <div className="results">
        {run.results.map((result) => (
          <div
            key={result.id}
            className={`result-card ${result.passed ? "pass" : "fail"}`}
          >
            <div className="result-header">
              <span className={`status ${result.passed ? "pass" : "fail"}`}>
                {result.passed ? "PASS" : "FAIL"}
              </span>
              <span className="case-id">{result.case_id}</span>
              <span className="score">Score: {result.score.toFixed(1)}</span>
            </div>

            <div className="result-body">
              <div className="field">
                <label>Prompt:</label>
                <pre>{result.prompt}</pre>
              </div>
              <div className="field">
                <label>Response:</label>
                <pre>{result.response}</pre>
              </div>
              {result.reasons.length > 0 && (
                <div className="field reasons">
                  <label>Failure Reasons:</label>
                  <ul>
                    {result.reasons.map((reason, i) => (
                      <li key={i}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
