import { useMemo } from "react";
import { scaleLinear } from "@visx/scale";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { GridRows, GridColumns } from "@visx/grid";
import { LinePath } from "@visx/shape";
import { curveLinear } from "@visx/curve";
import { Group } from "@visx/group";
import { useTooltip, TooltipWithBounds, defaultStyles } from "@visx/tooltip";

export type DataPointStatus = 'improvement' | 'minor_regression' | 'major_regression' | 'neutral';

export interface ChartDataPoint {
  revision: number;
  timestamp: Date;
  passRate: number; // 0-100
  model: string;
  systemPromptName?: string | null;
  systemPromptVersion?: string | null;
  gitCommitHash?: string | null;
  changeFromPrevious?: number | null; // percentage change from previous run
  status: DataPointStatus;
}

// Configurable thresholds for regression/improvement detection
export const THRESHOLDS = {
  improvement: 5,       // +5% or more = green
  minorRegression: -5,  // -5% to -10% = orange
  majorRegression: -10, // -10% or worse = red
};

// Status colors
const STATUS_COLORS: Record<DataPointStatus, string> = {
  improvement: '#22c55e',      // green
  minor_regression: '#f59e0b', // orange
  major_regression: '#ef4444', // red
  neutral: 'transparent',
};

const tooltipStyles = {
  ...defaultStyles,
  backgroundColor: "rgba(30, 30, 30, 0.95)",
  color: "white",
  padding: "12px 16px",
  borderRadius: "8px",
  fontSize: "13px",
  lineHeight: "1.5",
  boxShadow: "0 4px 12px rgba(0, 0, 0, 0.25)",
};

interface SuiteChartProps {
  data: ChartDataPoint[];
  width: number;
  height: number;
  margin?: { top: number; right: number; bottom: number; left: number };
}

export function SuiteChart({
  data,
  width,
  height,
  margin = { top: 20, right: 20, bottom: 40, left: 50 },
}: SuiteChartProps) {
  const {
    tooltipOpen,
    tooltipData,
    tooltipLeft,
    tooltipTop,
    showTooltip,
    hideTooltip,
  } = useTooltip<ChartDataPoint>();

  // Define dimensions
  const xMax = width - margin.left - margin.right;
  const yMax = height - margin.top - margin.bottom;

  // Scales - X-axis is revision-based (sequential)
  const xScale = useMemo(
    () =>
      scaleLinear<number>({
        range: [0, xMax],
        domain: data.length > 0 
          ? [Math.min(...data.map(d => d.revision)), 
             Math.max(...data.map(d => d.revision))]
          : [0, 1],
      }),
    [data, xMax]
  );

  const yScale = useMemo(
    () =>
      scaleLinear<number>({
        range: [yMax, 0],
        domain: [0, 100],
        nice: true,
      }),
    [yMax]
  );

  // Format datetime for tooltip
  const formatDateTime = (date: Date) => {
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (data.length === 0) {
    return (
      <svg width={width} height={height}>
        <text
          x={width / 2}
          y={height / 2}
          textAnchor="middle"
          fill="#666"
          fontSize="14"
        >
          No data available
        </text>
      </svg>
    );
  }

  return (
    <div style={{ position: "relative" }}>
      <svg width={width} height={height}>
        <Group left={margin.left} top={margin.top}>
          {/* Grid */}
          <GridRows
            scale={yScale}
            width={xMax}
            strokeDasharray="3,3"
            stroke="#e0e0e0"
            pointerEvents="none"
          />
          <GridColumns
            scale={xScale}
            height={yMax}
            strokeDasharray="3,3"
            stroke="#e0e0e0"
            pointerEvents="none"
          />

          {/* Line */}
          <LinePath<ChartDataPoint>
            data={data}
            x={(d) => xScale(d.revision)}
            y={(d) => yScale(d.passRate)}
            stroke="#3b82f6"
            strokeWidth={2}
            curve={curveLinear}
          />

          {/* Status indicator underlays (regression/improvement markers) */}
          {data.map((d, i) => 
            d.status !== 'neutral' && (
              <circle
                key={`status-${i}`}
                cx={xScale(d.revision)}
                cy={yScale(d.passRate)}
                r={10}
                fill={STATUS_COLORS[d.status]}
                opacity={0.3}
              />
            )
          )}

          {/* Data points */}
          {data.map((d, i) => (
            <circle
              key={i}
              cx={xScale(d.revision)}
              cy={yScale(d.passRate)}
              r={5}
              fill="#3b82f6"
              stroke="#fff"
              strokeWidth={2}
              style={{ cursor: "pointer" }}
              onMouseEnter={() => {
                showTooltip({
                  tooltipData: d,
                  tooltipLeft: xScale(d.revision) + margin.left,
                  tooltipTop: yScale(d.passRate) + margin.top - 10,
                });
              }}
              onMouseLeave={() => hideTooltip()}
            />
          ))}

          {/* Axes */}
          <AxisBottom
            top={yMax}
            scale={xScale}
            tickValues={data.map(d => d.revision)}
            tickFormat={(value) => `r${Math.round(value as number)}`}
            stroke="#666"
            tickStroke="#666"
            tickLabelProps={() => ({
              fill: "#666",
              fontSize: 11,
              textAnchor: "middle" as const,
            })}
          />
          <AxisLeft
            scale={yScale}
            numTicks={5}
            tickFormat={(value) => `${value}%`}
            stroke="#666"
            tickStroke="#666"
            tickLabelProps={() => ({
              fill: "#666",
              fontSize: 11,
              textAnchor: "end" as const,
              dx: -5,
            })}
          />
        </Group>
      </svg>

      {/* Tooltip */}
      {tooltipOpen && tooltipData && (
        <TooltipWithBounds
          top={tooltipTop}
          left={tooltipLeft}
          style={tooltipStyles}
        >
          <div style={{ marginBottom: "8px", fontWeight: 600, fontSize: "14px" }}>
            r{tooltipData.revision} — {tooltipData.passRate.toFixed(1)}% Pass Rate
            {tooltipData.changeFromPrevious !== null && tooltipData.changeFromPrevious !== undefined && (
              <span style={{ 
                marginLeft: "8px", 
                color: STATUS_COLORS[tooltipData.status],
                fontWeight: 500,
              }}>
                ({tooltipData.changeFromPrevious >= 0 ? '+' : ''}{tooltipData.changeFromPrevious.toFixed(1)}%)
              </span>
            )}
          </div>
          <div style={{ display: "grid", gap: "4px" }}>
            <div>
              <span style={{ color: "#9ca3af" }}>Model: </span>
              {tooltipData.model}
            </div>
            {tooltipData.systemPromptName && (
              <div>
                <span style={{ color: "#9ca3af" }}>System Prompt: </span>
                {tooltipData.systemPromptName}
                {tooltipData.systemPromptVersion && ` (${tooltipData.systemPromptVersion})`}
              </div>
            )}
            <div>
              <span style={{ color: "#9ca3af" }}>Commit: </span>
              <code style={{ fontFamily: "monospace", backgroundColor: "rgba(255,255,255,0.1)", padding: "1px 4px", borderRadius: "3px" }}>
                {tooltipData.gitCommitHash || "N/A"}
              </code>
            </div>
            <div>
              <span style={{ color: "#9ca3af" }}>Date: </span>
              {formatDateTime(tooltipData.timestamp)}
            </div>
          </div>
        </TooltipWithBounds>
      )}
    </div>
  );
}

