import { useMemo, useRef, useEffect, useState } from "react";
import { SuiteChart, type ChartDataPoint, type DataPointStatus, THRESHOLDS } from "./SuiteChart";
import { FailuresPanel } from "./FailuresPanel";
import { API_BASE_URL } from "../config";

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

interface TestCase {
  id: string;
  prompt: string;
  expected: Record<string, unknown>;
}

interface SuiteDetails {
  scorer: string;
  llm_criteria?: string | null;
  cases: TestCase[];
}

interface SuiteCardProps {
  suiteId: string;
  title: string;
  description?: string | null;
  scorer?: string;
  runs: Run[];
  featured?: boolean;
}

export function SuiteCard({ suiteId, title, description, scorer, runs, featured }: SuiteCardProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = useState(400);
  const [expanded, setExpanded] = useState(false);
  const [details, setDetails] = useState<SuiteDetails | null>(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  useEffect(() => {
    const updateWidth = () => {
      if (chartContainerRef.current) {
        const width = chartContainerRef.current.getBoundingClientRect().width;
        setChartWidth(Math.max(300, width));
      }
    };

    updateWidth();
    window.addEventListener("resize", updateWidth);
    return () => window.removeEventListener("resize", updateWidth);
  }, []);

  // Fetch details when expanded
  useEffect(() => {
    if (expanded && !details && !loadingDetails) {
      setLoadingDetails(true);
      fetch(`${API_BASE_URL}/api/suites/${suiteId}`)
        .then((res) => res.ok ? res.json() : null)
        .then((data) => {
          if (data) {
            setDetails({
              scorer: data.scorer || "rules",
              llm_criteria: data.llm_criteria,
              cases: data.cases || [],
            });
          }
        })
        .catch(() => {})
        .finally(() => setLoadingDetails(false));
    }
  }, [expanded, details, loadingDetails, suiteId]);

  // Calculate statistics including delta status
  const stats = useMemo(() => {
    if (runs.length === 0) {
      return {
        totalRuns: 0,
        averagePassRate: 0,
        latestPassRate: null as number | null,
        delta: null as number | null,
        deltaStatus: null as 'improvement' | 'regression' | 'no_change' | null,
      };
    }

    // Sort by revision (newest first already from API, but let's be explicit)
    const sortedByRevision = runs.slice().sort((a, b) => {
      if (a.revision != null && b.revision != null) {
        return b.revision - a.revision; // Newest first
      }
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });

    const passRates = runs.map(
      (run) => (run.passed / run.total) * 100
    );
    const averagePassRate =
      passRates.reduce((sum, rate) => sum + rate, 0) / passRates.length;
    
    // Latest and previous based on revision
    const latestRun = sortedByRevision[0];
    const previousRun = sortedByRevision[1];
    const latestPassRate = (latestRun.passed / latestRun.total) * 100;
    
    let delta: number | null = null;
    let deltaStatus: 'improvement' | 'regression' | 'no_change' | null = null;
    
    if (previousRun) {
      const previousPassRate = (previousRun.passed / previousRun.total) * 100;
      delta = latestPassRate - previousPassRate;
      
      if (delta >= THRESHOLDS.improvement) {
        deltaStatus = 'improvement';
      } else if (delta <= THRESHOLDS.majorRegression) {
        deltaStatus = 'regression';
      } else if (delta <= THRESHOLDS.minorRegression) {
        deltaStatus = 'regression';
      } else {
        deltaStatus = 'no_change';
      }
    }

    return {
      totalRuns: runs.length,
      averagePassRate,
      latestPassRate,
      delta,
      deltaStatus,
    };
  }, [runs]);

  // Prepare chart data (sorted by revision, oldest to newest) with regression/improvement status
  const chartData: ChartDataPoint[] = useMemo(() => {
    const sortedRuns = runs
      .slice()
      // Sort by revision if available, fallback to timestamp
      .sort((a, b) => {
        if (a.revision != null && b.revision != null) {
          return a.revision - b.revision;
        }
        return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      });

    // Helper to determine status based on change
    const getStatus = (change: number | null): DataPointStatus => {
      if (change === null) return 'neutral'; // First run
      if (change >= THRESHOLDS.improvement) return 'improvement';
      if (change <= THRESHOLDS.majorRegression) return 'major_regression';
      if (change <= THRESHOLDS.minorRegression) return 'minor_regression';
      return 'neutral';
    };

    return sortedRuns.map((run, index) => {
      const passRate = (run.passed / run.total) * 100;
      const previousPassRate = index > 0 
        ? (sortedRuns[index - 1].passed / sortedRuns[index - 1].total) * 100 
        : null;
      const changeFromPrevious = previousPassRate !== null 
        ? passRate - previousPassRate 
        : null;

      return {
        runId: run.id,
        revision: run.revision ?? 0,
        timestamp: new Date(run.timestamp),
        passRate,
        model: run.model,
        systemPromptName: run.system_prompt_name,
        gitCommitHash: run.git_commit_hash,
        changeFromPrevious,
        status: getStatus(changeFromPrevious),
      };
    });
  }, [runs]);

  const formatExpected = (expected: Record<string, unknown>): string => {
    if (Object.keys(expected).length === 0) return "—";
    return Object.entries(expected)
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key}: [${value.join(", ")}]`;
        }
        return `${key}: ${value}`;
      })
      .join(", ");
  };

  return (
    <div className={`suite-card${featured ? " suite-card-featured" : ""}`}>
      <div 
        className="suite-card-header suite-card-header-clickable"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="suite-card-header-content">
          <div className="suite-card-title-row">
            <h3>{title}</h3>
            {scorer && (
              <span className={`scorer-badge scorer-${scorer}`}>
                {scorer === "llm" ? "LLM Judge" : "Rule-based"}
              </span>
            )}
          </div>
          {description && <p className="suite-card-description">{description}</p>}
        </div>
        <span className={`suite-card-chevron ${expanded ? "expanded" : ""}`}>
          ▼
        </span>
      </div>

      {expanded && (
        <div className="suite-card-details">
          {loadingDetails ? (
            <div className="suite-card-loading">Loading details...</div>
          ) : details ? (
            <>
              {details.llm_criteria && (
                <div className="suite-card-criteria">
                  <div className="criteria-label">LLM Criteria:</div>
                  <pre className="criteria-content">{details.llm_criteria}</pre>
                </div>
              )}

              <div className="suite-card-cases">
                <div className="cases-label">Test Cases ({details.cases.length}):</div>
                <ul className="cases-list">
                  {details.cases.map((testCase) => (
                    <li key={testCase.id} className="case-item">
                      <div className="case-id">{testCase.id}</div>
                      <div className="case-prompt">{testCase.prompt}</div>
                      {details.scorer === "rules" && Object.keys(testCase.expected).length > 0 && (
                        <div className="case-expected">
                          Expected: {formatExpected(testCase.expected)}
                        </div>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <div className="suite-card-error">Failed to load details</div>
          )}
        </div>
      )}

      <div className="suite-card-stats">
        <div className="stat">
          <div className="stat-label">Total Runs</div>
          <div className="stat-value">{stats.totalRuns}</div>
        </div>
        <div className="stat">
          <div className="stat-label">Avg Pass Rate</div>
          <div className="stat-value">
            {stats.totalRuns > 0
              ? `${stats.averagePassRate.toFixed(1)}%`
              : "N/A"}
          </div>
        </div>
        <div className="stat">
          <div className="stat-label">Latest Pass Rate</div>
          <div className="stat-value">
            {stats.latestPassRate !== null
              ? `${stats.latestPassRate.toFixed(1)}%`
              : "N/A"}
          </div>
        </div>
        <div className="stat">
          <div className="stat-label">Change</div>
          <div className="stat-value">
            {stats.deltaStatus === null ? (
              <span className="delta-badge delta-na">—</span>
            ) : stats.deltaStatus === 'improvement' ? (
              <span className="delta-badge delta-improvement">
                ↑ IMPROVED
              </span>
            ) : stats.deltaStatus === 'regression' ? (
              <span className="delta-badge delta-regression">
                ↓ REGRESSION
              </span>
            ) : (
              <span className="delta-badge delta-no-change">
                → NO CHANGE
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="suite-card-chart" ref={chartContainerRef}>
        {chartData.length > 0 && (
          <SuiteChart
            data={chartData}
            width={chartWidth}
            height={200}
            margin={{ top: 20, right: 20, bottom: 40, left: 50 }}
            onPointClick={(runId) => setSelectedRunId(runId)}
          />
        )}
      </div>

      {/* Failures Panel */}
      {selectedRunId && (
        <FailuresPanel
          runId={selectedRunId}
          onClose={() => setSelectedRunId(null)}
        />
      )}
    </div>
  );
}
