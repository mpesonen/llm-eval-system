import { useMemo } from "react";
import { scaleTime, scaleLinear } from "@visx/scale";
import { AxisBottom, AxisLeft } from "@visx/axis";
import { GridRows, GridColumns } from "@visx/grid";
import { LinePath } from "@visx/shape";
import { curveLinear } from "@visx/curve";
import { Group } from "@visx/group";

export interface ChartDataPoint {
  timestamp: Date;
  passRate: number; // 0-100
}

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
            r={4}
            fill="#3b82f6"
            stroke="#fff"
            strokeWidth={2}
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
  );
}

