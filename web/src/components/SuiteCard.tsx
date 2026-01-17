import { useMemo, useRef, useEffect, useState } from "react";
import { SuiteChart, type ChartDataPoint } from "./SuiteChart";

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

  // Prepare chart data (sorted by timestamp, oldest to newest)
  const chartData: ChartDataPoint[] = useMemo(() => {
    return runs
      .slice()
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
      .map((run) => ({
        timestamp: new Date(run.timestamp),
        passRate: (run.passed / run.total) * 100,
        model: run.model,
        systemPromptName: run.system_prompt_name,
        systemPromptVersion: run.system_prompt_version,
      }));
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

