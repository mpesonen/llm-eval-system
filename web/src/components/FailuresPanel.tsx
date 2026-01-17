import { useEffect, useState } from "react";

interface FailureCase {
  id: string;
  case_id: string;
  prompt: string;
  response: string;
  passed: boolean;
  score: number;
  reasons: string[];
  system_prompt_name?: string | null;
}

interface RunDetails {
  id: string;
  suite_id: string;
  model: string;
  timestamp: string;
  system_prompt_name?: string | null;
  revision?: number | null;
  git_commit_hash?: string | null;
  results: FailureCase[];
}

interface FailuresPanelProps {
  runId: string;
  onClose: () => void;
}

export function FailuresPanel({ runId, onClose }: FailuresPanelProps) {
  const [runDetails, setRunDetails] = useState<RunDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetch(`http://localhost:8000/api/runs/${runId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch run details");
        return res.json();
      })
      .then((data) => {
        setRunDetails(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [runId]);

  const failures = runDetails?.results.filter((r) => !r.passed) || [];
  const totalCases = runDetails?.results.length || 0;

  const truncate = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + "…";
  };

  return (
    <>
      {/* Backdrop */}
      <div className="failures-panel-backdrop" onClick={onClose} />

      {/* Panel */}
      <div className="failures-panel">
        <div className="failures-panel-header">
          <div className="failures-panel-title">
            {runDetails && (
              <>
                <span className="failures-panel-revision">r{runDetails.revision}</span>
                <span className="failures-panel-count">
                  {failures.length} / {totalCases} Failed
                </span>
              </>
            )}
          </div>
          <button className="failures-panel-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="failures-panel-content">
          {loading && <div className="failures-panel-loading">Loading...</div>}
          {error && <div className="failures-panel-error">{error}</div>}
          
          {!loading && !error && failures.length === 0 && (
            <div className="failures-panel-success">
              ✓ All {totalCases} cases passed!
            </div>
          )}

          {!loading && !error && failures.length > 0 && (
            <div className="failures-list">
              {failures.map((failure) => (
                <div key={failure.id} className="failure-card">
                  <div className="failure-card-header">
                    <span className="failure-icon">✗</span>
                    <span className="failure-case-id">{failure.case_id}</span>
                  </div>
                  
                  <div className="failure-section">
                    <div className="failure-label">Prompt</div>
                    <div className="failure-text">{truncate(failure.prompt, 200)}</div>
                  </div>
                  
                  <div className="failure-section">
                    <div className="failure-label">Response</div>
                    <div className="failure-text failure-response">
                      {truncate(failure.response, 300)}
                    </div>
                  </div>
                  
                  {failure.reasons.length > 0 && (
                    <div className="failure-section">
                      <div className="failure-label">Reasons</div>
                      <ul className="failure-reasons">
                        {failure.reasons.map((reason, i) => (
                          <li key={i}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {runDetails && (
          <div className="failures-panel-footer">
            <div><span className="footer-label">Model:</span> {runDetails.model}</div>
            {runDetails.system_prompt_name && (
              <div><span className="footer-label">Prompt:</span> {runDetails.system_prompt_name}</div>
            )}
            {runDetails.git_commit_hash && (
              <div><span className="footer-label">Commit:</span> <code>{runDetails.git_commit_hash}</code></div>
            )}
          </div>
        )}
      </div>
    </>
  );
}
