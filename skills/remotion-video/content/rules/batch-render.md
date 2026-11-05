---
name: batch-render
description: Batch rendering, parameterized videos, data-driven automation.
tags: batch, render, automation, data-driven, template, cron
---

# Batch Rendering & Automation

## Parameterized Composition

```typescript
export const DataReportVideo: React.FC<{
  title: string;
  quarter: string;
  revenue: number;
  growth: number;
  chartData: number[];
}> = ({ title, quarter, revenue, growth, chartData }) => (
  <div style={{ background: "#0f0f23" }}>
    <AnimatedTitle text={title} start={0} />
    <AnimatedTitle text={quarter + " Quarterly Report"} start={30} />
    <AnimatedTitle text={"Revenue: " + revenue + "M"} start={60} />
    <BarChart data={chartData} startFrame={120} />
  </div>
);
```

## Batch Props Generator

```python
# generate_batch_props.py
import json, random
quarters = ["Q1", "Q2", "Q3", "Q4"]
data = [
  {"title": f"{q} Quarterly Report", "quarter": q,
   "revenue": random.randint(100, 500),
   "growth": random.randint(5, 30),
   "chartData": [random.randint(50, 200) for _ in range(6)]}
  for q in quarters
]
with open("batch_props.json", "w") as f:
    json.dump(data, f)
```

## Batch Render Script

```bash
#!/bin/bash
for row in $(cat batch_props.json | jq -c '.[]'); do
    ID=$(echo "$row" | jq -r '.id // "Video"')
    npx remotion render DataReportVideo "output/${ID}.mp4"       --props="$row" --fps=30 --codec=h264
done
```

## Cron Automation

```python
cron(action="add", job={
    "name": "Weekly Report Auto-Render",
    "schedule": {"kind": "cron", "expr": "0 8 * * 1", "tz": "Asia/Shanghai"},
    "payload": {
        "kind": "agentTurn",
        "message": "1. Read latest data ./data/weekly.json "
                   "2. Update batch_props.json "
                   "3. Run batch_remotion.sh "
                   "4. Upload to CDN and notify me",
    },
    "sessionTarget": "isolated",
    "delivery": {"mode": "announce"},
    "enabled": True,
})
```
