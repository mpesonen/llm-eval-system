import { useMemo, useRef, useEffect, useState } from "react";
import { SuiteChart, type ChartDataPoint, type DataPointStatus, THRESHOLDS } from "./SuiteChart";

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

interface SuiteCardProps {
  suiteId: string;
  title: string;
  description?: string | null;
  runs: Run[];
  featured?: boolean;
}

export function SuiteCard({ title, description, runs, featured }: SuiteCardProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = useState(400);

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

  // Calculate statistics
  const stats = useMemo(() => {
    if (runs.length === 0) {
      return {
        totalRuns: 0,
        averagePassRate: 0,
        latestPassRate: null as number | null,
      };
    }

    const passRates = runs.map(
      (run) => (run.passed / run.total) * 100
    );
    const averagePassRate =
      passRates.reduce((sum, rate) => sum + rate, 0) / passRates.length;
    // API returns runs sorted newest first, so latest is the first one
    const latestPassRate = passRates[0];

    return {
      totalRuns: runs.length,
      averagePassRate,
      latestPassRate,
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

  return (
    <div className={`suite-card${featured ? " suite-card-featured" : ""}`}>
      <div className="suite-card-header">
        <h3>{title}</h3>
        {description && <p className="suite-card-description">{description}</p>}
      </div>

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
      </div>

      <div className="suite-card-chart" ref={chartContainerRef}>
        {chartData.length > 0 && (
          <SuiteChart
            data={chartData}
            width={chartWidth}
            height={200}
            margin={{ top: 20, right: 20, bottom: 40, left: 50 }}
          />
        )}
      </div>
    </div>
  );
}

