import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { formatLargeNumber } from "../../utils/dataTransform";

export default function ComparisonChart({ data, title, dataKeys = [] }) {
  if (!data || data.length === 0) return null;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="chart-tooltip">
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {`${entry.name}: ${formatLargeNumber(entry.value)}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  const COLORS = ["#1976d2", "#42a5f5", "#66bb6a", "#ffa726", "#ef5350"];

  return (
    <div className="card">
      <h3>{title}</h3>
      <div style={{ width: "100%", height: 300, marginTop: "20px" }}>
        <ResponsiveContainer>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis tickFormatter={(value) => formatLargeNumber(value)} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {dataKeys.map((key, index) => (
              <Bar
                key={key}
                dataKey={key}
                fill={COLORS[index % COLORS.length]}
                name={key.replace(/_/g, " ").toUpperCase()}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

