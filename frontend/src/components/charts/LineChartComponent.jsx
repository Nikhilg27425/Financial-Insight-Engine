import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { formatLargeNumber } from "../../utils/dataTransform";

export default function LineChartComponent({ data, dataKey, title, color = "#1976d2" }) {
  if (!data || data.length === 0) return null;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          <p>{`${payload[0].name}: ${formatLargeNumber(payload[0].value)}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <h3>{title}</h3>
      <div style={{ width: "100%", height: 300, marginTop: "20px" }}>
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" />
            <YAxis tickFormatter={(value) => formatLargeNumber(value)} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Line
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={3}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

