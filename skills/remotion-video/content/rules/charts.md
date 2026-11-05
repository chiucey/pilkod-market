---
name: charts
description: Data chart animations: bar, line, pie, stock charts in Remotion.
tags: chart, data, animation, bar, line, pie, svg
---

# Data Chart Animation

## Bar Chart

```typescript
const BarChart: React.FC<{ data: number[]; labels: string[] }> = ({ data, labels }) => {
  const frame = useCurrentFrame();
  const max = Math.max(...data);

  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 40, height: 400 }}>
      {data.map((value, i) => {
        const barStart = i * 15;
        const progress = interpolate(frame, [barStart, barStart + 30], [0, 1]);

        return (
          <div key={i} style={{ textAlign: "center" }}>
            <div style={{
              width: 60,
              height: interpolate(progress, [0, 1], [0, (value / max) * 350]),
              background: `hsl(${200 + i * 20}, 80%, 60%)`,
              borderRadius: "8px 8px 0 0",
              margin: "0 auto",
            }} />
            <div style={{ fontSize: 24, color: "white", marginTop: 8 }}>{value}</div>
            <div style={{ fontSize: 18, color: "#aaa" }}>{labels[i]}</div>
          </div>
        );
      })}
    </div>
  );
};
```

## Line Chart

```typescript
const LineChart: React.FC<{ points: [number, number][] }> = ({ points }) => {
  const frame = useCurrentFrame();
  const linePath = points.map(([x, y], i) =>
    `${i === 0 ? "M" : "L"} ${x} ${y}`
  ).join(" ");
  const dashOffset = interpolate(frame, [0, points.length * 10], [1000, 0]);

  return (
    <svg width="800" height="400">
      <path d={linePath} fill="none" stroke="#4facfe"
        strokeWidth="3" strokeDasharray={1000} strokeDashoffset={dashOffset} />
    </svg>
  );
};
```

## Animation Curves

```typescript
// Smooth ease-in-out
interpolate(frame, [inStart, inStart + 45], [0, 1], {
  easing: Easing.bezier(0.25, 0.1, 0.25, 1),
});

// Bounce spring
spring({ frame, fps, config: { damping: 8, stiffness: 90 } });
```
