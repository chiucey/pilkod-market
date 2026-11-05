# Commodity Data Sources Reference

## Public Data Sources by Category

### Dairy Products

| Source | Data Type | Access Method | Update Frequency |
|--------|-----------|---------------|------------------|
| USDA FRED | PPI, Price Index | Direct CSV download | Monthly |
| USDA ERS | Supply/Demand | Web scraping | Monthly |
| Global Dairy Trade | Auction Prices | API (requires key) | Bi-weekly |

**FRED Series IDs:**
- `WPU023307`: Raw Liquid Whey (2012-present)
- `WFDNSX02USM365`: Dairy Products Index
- `PCU3115113111`: Whey (Dried) - Monthly

### China-Specific Data

| Source | Data Type | Access Method | Notes |
|--------|-----------|---------------|-------|
| China Customs | Import/Export | customs.gov.cn | May require login |
| National Bureau of Statistics | PPI, Production | stats.gov.cn | Free access |
| Trade News Sources | Aggregate data | News aggregation | Good for historical |

**China Whey Import Data Structure:**
```json
{
  "date": "2026-03",
  "quantity_ton": 72000,
  "amount_usd": 97500000,
  "unit_price_usd": 1354.17
}
```

### Energy Commodities

- **EIA (US Energy Information Administration)**: api.eia.gov
- **OPEC**: Monthly oil bulletins
- **IEA**: iea.org (requires registration)

### Metals

- **LME (London Metal Exchange)**: lme.com
- **USGS Minerals**: minerals.usgs.gov
- **Metal Bulletin**: benchmarkmineral.com (paid)

## FRED API Usage

### Without API Key (Recommended for simple use)
```python
import pandas as pd

series_id = "WPU023307"
url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
df = pd.read_csv(url, parse_dates=['DATE'])
df.columns = ['date', 'price']
```

### With API Key
```python
import requests

api_key = "YOUR_API_KEY"
series_id = "WPU023307"
url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
```

## Data Quality Indicators

When building dashboards, indicate data quality:

1. **Official Source**: Direct government/statistics bureau
2. **Verified Third-Party**: Major news, Bloomberg, Reuters
3. **Estimated**: Calculated from related indicators
4. **Simulated**: Based on trends (clearly label)
