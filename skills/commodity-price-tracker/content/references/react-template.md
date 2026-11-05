# React Dashboard Template

## Component Structure

```tsx
import { useState, useEffect } from 'react';
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';

interface PriceData {
  date: string;
  price: number;
  change?: number;
  changePercent?: number;
}

interface Alert {
  date: string;
  type: 'up' | 'down';
  percent: number;
  message: string;
}

// Volatility detection function
function detectVolatility(data: PriceData[], threshold: number = 5): Alert[] {
  const alerts: Alert[] = [];

  for (let i = 1; i < data.length; i++) {
    const prev = data[i - 1];
    const curr = data[i];
    const changePercent = ((curr.price - prev.price) / prev.price) * 100;

    if (Math.abs(changePercent) >= threshold) {
      alerts.push({
        date: curr.date,
        type: changePercent > 0 ? 'up' : 'down',
        percent: Math.abs(changePercent),
        message: `${curr.date}: ${changePercent > 0 ? '+' : ''}${changePercent.toFixed(1)}%`
      });
    }
  }

  return alerts;
}

// Price trend chart
function PriceTrendChart({ data }: { data: PriceData[] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
            <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
          </linearGradient>
        </defs>
        <XAxis dataKey="date" stroke="#94a3b8" />
        <YAxis stroke="#94a3b8" />
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: 'none' }} />
        <Area type="monotone" dataKey="price" stroke="#22c55e" fill="url(#colorPrice)" />
      </AreaChart>
    </ResponsiveContainer>
  );
}

// Alert list component
function AlertList({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="space-y-2">
      {alerts.map((alert, idx) => (
        <div
          key={idx}
          className={`p-3 rounded-lg flex items-center gap-3 ${
            alert.type === 'up' ? 'bg-red-900/30' : 'bg-green-900/30'
          }`}
        >
          <span className={alert.type === 'up' ? 'text-red-400' : 'text-green-400'}>
            {alert.type === 'up' ? '↑' : '↓'}
          </span>
          <span className="text-gray-300">{alert.message}</span>
        </div>
      ))}
    </div>
  );
}

// Stats summary
function StatsSummary({ data }: { data: PriceData[] }) {
  const prices = data.map(d => d.price);
  return {
    latest: prices[prices.length - 1],
    min: Math.min(...prices),
    max: Math.max(...prices),
    avg: prices.reduce((a, b) => a + b, 0) / prices.length
  };
}
```

## Styling Guidelines

### Color Theme
- Primary (positive): `#22c55e` (green-500)
- Secondary (negative): `#ef4444` (red-500)
- Background: `#0f172a` (slate-900)
- Card: `#1e293b` (slate-800)
- Text: `#e2e8f0` (slate-200)

### Responsive Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

## Cron Job Setup

For daily data updates:

```python
# scripts/update_data.py
import json
import requests
from datetime import datetime

FRED_SERIES = "WPU023307"
DATA_FILE = "public/price_data.json"

def fetch_fred_data():
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={FRED_SERIES}"
    # Fetch and process data...
    return processed_data

def check_volatility(data, threshold=5):
    alerts = []
    # Detection logic...
    return alerts

if __name__ == "__main__":
    data = fetch_fred_data()
    alerts = check_volatility(data)
    # Save to JSON and send notifications...
```

Cron expression for daily at 8 AM:
```
0 8 * * *
```
