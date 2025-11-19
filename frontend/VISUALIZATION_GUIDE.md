# Dashboard Visualization Guide

## Current Status

The dashboard is now fixed and will no longer show a white screen. It safely handles:
- Missing or empty data
- Different data formats
- Loading and error states
- Empty visualizations

## What Data Structure is Expected

The dashboard expects data from the `/analyze/{file_id}` endpoint in this format:

```json
{
  "balance_sheet": [
    { "name": "Item Name", "value": 12345 }
  ],
  "pnl": {
    "revenue": 100000,
    "expenses": 50000
  },
  "cash_flow": {
    "operating": 20000,
    "investing": -5000
  },
  "kpis": {
    "net_profit": 50000,
    "revenue_growth": 15.5
  },
  "trends": {
    "revenue_trend": {
      "2021": 400000,
      "2022": 600000,
      "2023": 720000
    }
  }
}
```

## Visualization Components Available

The dashboard currently supports:

### 1. **KPI Cards** (`kpi-cards-grid`)
- Displays key performance indicators as cards
- Shows when `analysisData.kpis` exists and has data
- **File**: Already implemented in `DashboardPage.jsx`

### 2. **Revenue Trends Chart** (Area Chart)
- Shows revenue over time
- Requires `trends.revenue_trend` object with period-value pairs
- **File**: Already implemented in `DashboardPage.jsx`

### 3. **KPI Bar Chart**
- Bar chart showing all KPIs
- Requires `kpis` object with numeric values
- **File**: Already implemented in `DashboardPage.jsx`

### 4. **Financial Tables**
- Balance Sheet table
- Profit & Loss table
- Cash Flow table
- **Files**: Already implemented in `DashboardPage.jsx`

## What You Need to Do

### Option 1: Ensure Backend Returns Correct Format

Make sure your backend's `analyze` endpoint returns data in the expected format:

**Backend File**: `backend/app/routes/analysis.py`

The endpoint should return:
- `kpis`: Object with key-value pairs (values should be numbers)
- `trends`: Object with `revenue_trend` containing period-value pairs
- `balance_sheet`: Array of objects with `name` and `value` properties
- `pnl`: Object with financial metrics
- `cash_flow`: Object with cash flow metrics

### Option 2: Create Data Transformation Component

If your backend returns data in a different format, create a transformation utility:

**New File**: `frontend/src/utils/dataTransform.js`

```javascript
export const transformAnalysisData = (rawData) => {
  // Transform your backend data format to the expected format
  return {
    kpis: transformKPIs(rawData),
    trends: transformTrends(rawData),
    balance_sheet: transformBalanceSheet(rawData),
    pnl: transformPNL(rawData),
    cash_flow: transformCashFlow(rawData)
  };
};
```

Then update `DashboardPage.jsx` to use this transformation.

### Option 3: Add Custom Visualization Components

If you need additional visualizations, create new components:

**New Files**:
- `frontend/src/components/charts/LineChartComponent.jsx`
- `frontend/src/components/charts/PieChartComponent.jsx`
- `frontend/src/components/charts/ComparisonChart.jsx`

## Current Implementation Files

All visualization code is in:
- **Main Dashboard**: `frontend/src/pages/DashboardPage.jsx`
- **Styles**: `frontend/src/styles.css` (look for `.kpi-cards-grid`, `.kpi-card`, etc.)
- **API Utils**: `frontend/src/utils/api.js`

## Testing Visualizations

1. Upload a PDF file
2. Wait for analysis to complete
3. Navigate to Dashboard
4. The dashboard will:
   - Show KPI cards if `kpis` data exists
   - Show charts if trend/KPI data exists
   - Show tables if financial data exists
   - Show a message with raw data if no visualizations are possible

## Debugging

If visualizations don't appear:

1. Check browser console for errors
2. Click "View raw analysis data" in the dashboard to see what data structure you're getting
3. Verify the data matches the expected format above
4. Check that numeric values are actually numbers, not strings

## Next Steps

1. **Verify backend data format** - Check what your `/analyze/{file_id}` endpoint actually returns
2. **Test with real data** - Upload a PDF and check the raw data output
3. **Transform if needed** - Create transformation utilities if data format differs
4. **Add custom charts** - Create additional visualization components as needed

The dashboard is now safe and won't crash - it will gracefully handle any data format and show what's available!

