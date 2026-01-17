import { useMemo } from "react";
import { scaleTime, scaleLinear } from "@visx/scale";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { GridRows, GridColumns } from "@visx/grid";
import { LinePath } from "@visx/shape";
import { curveLinear } from "@visx/curve";
import { Group } from "@visx/group";
import { useTooltip, TooltipWithBounds, defaultStyles } from "@visx/tooltip";

export interface ChartDataPoint {
  timestamp: Date;
  passRate: number; // 0-100
  model: string;
  systemPromptName?: string | null;
  systemPromptVersion?: string | null;
}

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

  // Scales
  const xScale = useMemo(
    () =>
      scaleTime<number>({
        range: [0, xMax],
        domain: data.length > 0 
          ? [new Date(Math.min(...data.map(d => d.timestamp.getTime()))), 
             new Date(Math.max(...data.map(d => d.timestamp.getTime())))]
          : [new Date(), new Date()],
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

  // Format date for x-axis
  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

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
            x={(d) => xScale(d.timestamp)}
            y={(d) => yScale(d.passRate)}
            stroke="#3b82f6"
            strokeWidth={2}
            curve={curveLinear}
          />

          {/* Data points */}
          {data.map((d, i) => (
            <circle
              key={i}
              cx={xScale(d.timestamp)}
              cy={yScale(d.passRate)}
              r={5}
              fill="#3b82f6"
              stroke="#fff"
              strokeWidth={2}
              style={{ cursor: "pointer" }}
              onMouseEnter={() => {
                showTooltip({
                  tooltipData: d,
                  tooltipLeft: xScale(d.timestamp) + margin.left,
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
            numTicks={Math.min(5, data.length)}
            tickFormat={(value) => formatDate(value as Date)}
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
            {tooltipData.passRate.toFixed(1)}% Pass Rate
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
              <span style={{ color: "#9ca3af" }}>Date: </span>
              {formatDateTime(tooltipData.timestamp)}
            </div>
          </div>
        </TooltipWithBounds>
      )}
    </div>
  );
}

