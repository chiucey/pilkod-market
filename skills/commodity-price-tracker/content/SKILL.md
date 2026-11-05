---
name: commodity-price-tracker
description: Track commodity raw material prices with trend visualization and volatility alerts. Use when users ask to monitor prices, set up procurement alerts, or create commodity dashboards for enterprise purchasing. Triggers include: "追踪XX价格", "原材料价格趋势", "商品波动提醒", "采购价格监控", "track commodity prices", "monitor raw material costs".
---

# Commodity Price Tracker

Track raw material prices for enterprise procurement with automated alerts.

## Core Workflow

### 1. Data Source Discovery

Identify public data sources based on commodity type:

| Commodity Type | Primary Source | API/URL |
|----------------|----------------|---------|
| Agricultural | USDA, FAO | fred.stlouisfed.org |
| Energy | EIA, IEA | api.eia.gov |
| Metals | USGS, LME | lme.com |
| China-specific | Customs, NBS | customs.gov.cn |
| General PPI | FRED (US) | fred.stlouisfed.org |

**Key FRED Series for Whey Protein:**
- `WPU023307`: Raw Liquid Whey (US PPI)
- `WFDNSX02USM365`: Dairy Products

### 2. Data Extraction

For FRED data without API key:
```
https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}
```

For China customs data:
- Use news sources when direct access unavailable
- Aggregate from multiple reliable sources
- Document data quality and limitations

### 3. Volatility Detection

Algorithm for price fluctuation alerts:

```
threshold = 5%  # configurable
for each new_price in price_series:
    change_percent = (new_price - previous_price) / previous_price * 100
    if abs(change_percent) >= threshold:
        trigger_alert(new_price, change_percent)
```

### 4. React Dashboard Template

Structure for commodity tracker dashboard:

```tsx
interface PriceData {
  date: string;
  price: number;
  quantity?: number;
  change?: number;
  changePercent?: number;
}

interface Alert {
  date: string;
  type: 'up' | 'down';
  percent: number;
  message: string;
}

// Dashboard components:
// 1. Header: Commodity name, latest price, trend indicator
// 2. Chart: AreaChart (price trend) or BarChart (monthly changes)
// 3. Alerts: List of volatility events exceeding threshold
// 4. Stats: Min/Max/Avg prices, total alerts count
```

## Output Format

Deploy as React app with:
- Recharts for visualization (AreaChart, BarChart, LineChart)
- Tailwind CSS for styling
- Green theme for positive trends, red for negative

## Validation Checklist

- [ ] Data source is publicly accessible
- [ ] Price data has date and numeric value
- [ ] Volatility alerts trigger at configured threshold
- [ ] Charts display correctly with proper axis labels
- [ ] Dashboard is mobile-responsive
- [ ] Cron job scheduled for daily updates (if applicable)

## References

- `references/data-sources.md` - Detailed source list by commodity
- `references/react-template.md` - Dashboard component template
