import { useState, useEffect, useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import {
  BarChart,
  Bar,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import { api } from "../utils/api";
import {
  transformAnalysisData,
  prepareTrendDataForChart,
  formatLargeNumber,
} from "../utils/dataTransform";
import LineChartComponent from "../components/charts/LineChartComponent";
import PieChartComponent from "../components/charts/PieChartComponent";
import ComparisonChart from "../components/charts/ComparisonChart";

export default function DashboardPage() {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [files, setFiles] = useState([]);

  // ========== SAFETY HELPERS ==========
  const safeNumber = (v) =>
    typeof v === "number" && !Number.isNaN(v) && Number.isFinite(v);

  const shortenLabel = (label, max = 14) =>
    typeof label === "string" && label.length > max
      ? `${label.slice(0, max)}…`
      : label;

  const formatKpiLabel = (key) => key.replace(/_/g, " ").toUpperCase();

  // ========== LOAD FILE LIST ==========
  useEffect(() => {
    loadFiles();
  }, []);

  const loadFiles = async () => {
    try {
      const fileList = await api.getFiles();
      setFiles(fileList);

      const fileIdFromUrl = searchParams.get("fileId");
      if (fileList.length > 0) {
        setSelectedFileId(fileIdFromUrl || fileList[0].id);
      } else {
        setLoading(false);
      }
    } catch (err) {
      console.error("Failed to load files:", err);
      setError("Failed to load files. Please upload a file first.");
      setLoading(false);
    }
  };

  // ========== SELECT FILE BASED ON URL ==========
  useEffect(() => {
    const fileIdFromUrl = searchParams.get("fileId");
    if (fileIdFromUrl) {
      setSelectedFileId(fileIdFromUrl);
    }
  }, [searchParams]);

  // ========== LOAD ANALYSIS FOR SELECTED FILE ==========
  useEffect(() => {
    if (selectedFileId) {
      loadAnalysisData(selectedFileId);
    }
  }, [selectedFileId]);

  const loadAnalysisData = async (fileId) => {
    setLoading(true);
    setError(null);

    try {
      const rawData = await api.analyzeFile(fileId);
      const transformed = transformAnalysisData(rawData);
      setAnalysisData(transformed);
    } catch (err) {
      console.error("Failed to load analysis:", err);
      setError(err.message || "Failed to load analysis data");
      setAnalysisData(null);
    } finally {
      setLoading(false);
    }
  };

  // ========== PREPARE CHART DATA ==========
  const trendData = useMemo(() => {
    if (!analysisData?.trends) return [];
    return prepareTrendDataForChart(analysisData.trends).filter((d) =>
      safeNumber(d.revenue)
    );
  }, [analysisData]);

  const numericKpis = useMemo(() => {
    if (!analysisData?.kpis) return [];
    return Object.entries(analysisData.kpis || {}).filter(
      ([, value]) => safeNumber(value)
    );
  }, [analysisData]);

  const isFinancialMetric = (key, value) => {
    const lower = key.toLowerCase();
    const keywords = [
      "revenue",
      "income",
      "profit",
      "asset",
      "liabil",
      "equity",
      "cash",
      "capital",
      "expense",
      "turnover",
      "total",
    ];
    return (
      keywords.some((k) => lower.includes(k)) ||
      Math.abs(value) >= 1e6 ||
      key.includes("total")
    );
  };

  const financialKpiData = useMemo(
    () =>
      numericKpis
        .filter(([key, value]) => isFinancialMetric(key, value))
        .map(([key, value]) => ({ name: formatKpiLabel(key), value })),
    [numericKpis]
  );

  const ratioKpiData = useMemo(
    () =>
      numericKpis
        .filter(([key, value]) => !isFinancialMetric(key, value))
        .map(([key, value]) => ({
          name: formatKpiLabel(key),
          value,
          unit: key.includes("_pct") ? "%" : "",
        })),
    [numericKpis]
  );

  const safeBalanceSheet = useMemo(() => {
    return (analysisData?.balance_sheet || []).filter((item) =>
      safeNumber(item?.value)
    );
  }, [analysisData]);

  const safePnL = useMemo(() => {
    if (!analysisData?.pnl) return {};
    return Object.fromEntries(
      Object.entries(analysisData.pnl).filter(([_, v]) => safeNumber(v))
    );
  }, [analysisData]);

  const safeCashFlow = useMemo(() => {
    if (!analysisData?.cash_flow) return {};
    return Object.fromEntries(
      Object.entries(analysisData.cash_flow).filter(([_, v]) => safeNumber(v))
    );
  }, [analysisData]);

  const hasVisualizations =
    trendData.length > 0 ||
    financialKpiData.length > 0 ||
    ratioKpiData.length > 0 ||
    safeBalanceSheet.length > 0 ||
    Object.keys(safePnL).length > 0 ||
    Object.keys(safeCashFlow).length > 0;

  // ========== RENDER STATES ==========
  if (loading && !analysisData) {
    return (
      <div className="page">
        <div className="page-header">
          <h2>Insights Dashboard</h2>
          <p className="muted">Loading financial insights...</p>
        </div>
        <div className="card">
          <div className="loading-spinner">Loading...</div>
        </div>
      </div>
    );
  }

  if (error && !analysisData) {
    return (
      <div className="page">
        <div className="page-header">
          <h2>Insights Dashboard</h2>
        </div>
        <div className="card">
          <div className="alert alert-error">{error}</div>
          {files.length === 0 && <p>Please upload a file first.</p>}
        </div>
      </div>
    );
  }

  if (!analysisData) {
    return (
      <div className="page">
        <div className="page-header">
          <h2>Insights Dashboard</h2>
        </div>
        <div className="card">No analysis data available.</div>
      </div>
    );
  }

  // ========== MAIN DASHBOARD UI ==========
  return (
    <div className="page">
      <div className="page-header">
        <h2>Insights Dashboard</h2>
        <p className="muted">Key financial metrics and trends</p>

        {files.length > 0 && (
          <select
            className="file-selector"
            value={selectedFileId || ""}
            onChange={(e) => setSelectedFileId(e.target.value)}
            style={{
              marginTop: "12px",
              padding: "8px 12px",
              borderRadius: "8px",
              border: "1px solid #cbd5e1",
            }}
          >
            {files.map((file) => (
              <option key={file.id} value={file.id}>
                {file.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* KPI Cards */}
      {numericKpis.length > 0 && (
        <div className="kpi-cards-grid">
          {numericKpis.map(([key, value]) => (
            <div key={key} className="kpi-card">
              <div className="kpi-card-label">{key.replace(/_/g, " ")}</div>
              <div className="kpi-card-value">
                {key.includes("_pct") || key.includes("ratio")
                  ? `${value.toFixed(2)}${key.includes("_pct") ? "%" : ""}`
                  : formatLargeNumber(value)}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Trend Chart */}
      {trendData.length > 0 && (
        <div className="card">
          <h3>Revenue Trends</h3>
          <div style={{ width: "100%", height: 300, marginTop: 20 }}>
            <ResponsiveContainer>
              <AreaChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="period"
                  tickFormatter={(v) => shortenLabel(v, 18)}
                />
                <YAxis tickFormatter={(v) => formatLargeNumber(v)} />
                <Tooltip formatter={(v) => formatLargeNumber(v)} />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#1976d2"
                  fill="#1976d2"
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Financial KPI Bar Chart */}
      {financialKpiData.length > 0 && (
        <div className="card">
          <h3>Financial KPIs</h3>
          <div style={{ width: "100%", height: 320, marginTop: 20 }}>
            <ResponsiveContainer>
              <BarChart data={financialKpiData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="name"
                  tickFormatter={(v) => shortenLabel(v, 16)}
                />
                <YAxis tickFormatter={(v) => formatLargeNumber(v)} />
                <Tooltip formatter={(v) => formatLargeNumber(v)} />
                <Bar dataKey="value" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Ratio KPI Chart */}
      {ratioKpiData.length > 0 && (
        <div className="card">
          <h3>Ratio & Efficiency KPIs</h3>
          <div style={{ width: "100%", height: ratioKpiData.length * 45 }}>
            <ResponsiveContainer>
              <BarChart data={ratioKpiData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  type="number"
                  tickFormatter={(v) => Number(v).toFixed(2)}
                />
                <YAxis type="category" dataKey="name" width={180} />
                <Tooltip />
                <Bar dataKey="value" fill="#f97316" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Balance sheet pie */}
      {safeBalanceSheet.length > 0 && (
        <PieChartComponent
          title="Balance Sheet Distribution"
          data={safeBalanceSheet.slice(0, 6)}
        />
      )}

      {/* P&L Comparison */}
      {Object.keys(safePnL).length > 0 && (
        <ComparisonChart
          title="Profit & Loss Overview"
          data={[
            {
              name: "Financial Metrics",
              ...Object.fromEntries(
                Object.entries(safePnL).map(([k, v]) => [
                  k.replace(/_/g, " "),
                  v,
                ])
              ),
            },
          ]}
          dataKeys={Object.keys(safePnL)}
        />
      )}

      {/* Balance Sheet Line Graph */}
      {safeBalanceSheet.length > 0 && (
        <LineChartComponent
          title="Balance Sheet Items Trend"
          color="#66bb6a"
          data={safeBalanceSheet.slice(0, 10).map((item, idx) => ({
            period: item.name || `Item ${idx + 1}`,
            value: item.value,
          }))}
          dataKey="value"
        />
      )}

      {/* Raw Data (fallback) */}
      {!hasVisualizations && (
        <div className="card">
          <h3>Analysis Data Available</h3>
          <p className="muted">
            No charts could be drawn — dataset structure may not match expected format.
          </p>

          <details>
            <summary>View raw analysis JSON</summary>
            <pre className="result-json">
              {JSON.stringify(analysisData, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}
