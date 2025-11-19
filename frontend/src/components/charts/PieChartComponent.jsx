import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { formatLargeNumber } from "../../utils/dataTransform";

const COLORS = ["#1976d2", "#42a5f5", "#66bb6a", "#ffa726", "#ef5350", "#ab47bc", "#26a69a"];

export default function PieChartComponent({ data, title, dataKey = "value", nameKey = "name" }) {
  if (!data || data.length === 0) return null;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div className="chart-tooltip">
          <p>{`${data.name}: ${formatLargeNumber(data.value)}`}</p>
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
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey={dataKey}
              nameKey={nameKey}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

