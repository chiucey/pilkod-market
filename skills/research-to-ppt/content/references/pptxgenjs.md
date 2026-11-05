# PptxGenJS API Reference

## Setup

```javascript
const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";  // 10" x 5.625"
pres.title = "Research Report";
pres.author = "MiniMax Agent";
```

## Theme Object Contract

```javascript
const theme = {
  primary: "1A365D",    // Darkest - titles
  secondary: "2D3748",  // Dark accent - body text
  accent: "C9A227",     // Mid-tone - highlights
  light: "E2E8F0",      // Light accent
  bg: "FFFFFF"          // Background
};
```

## Basic Elements

### Text
```javascript
slide.addText("Text content", {
  x: 0.5, y: 0.5, w: 4, h: 1,
  fontSize: 24,
  fontFace: "Arial",
  color: "1A365D",
  bold: true,
  italic: false,
  align: "left",        // left, center, right
  valign: "top",        // top, middle, bottom
  bullet: true,
  lineSpacingMultiple: 1.4
});
```

### Shapes
```javascript
// Rectangle
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "C9A227" },
  line: { color: "1A365D", width: 1 }
});

// Rounded Rectangle
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "38A169" },
  rectRadius: 0.2
});

// Oval (for badges)
slide.addShape(pres.shapes.OVAL, {
  x: 8.5, y: 4.8, w: 0.5, h: 0.5,
  fill: { color: "C9A227" }
});
```

### Images
```javascript
slide.addImage("path/to/image.png", {
  x: 0.5, y: 1.5, w: 9, h: 3.5,
  fit: "contain"       // contain, cover, crop
});
```

## Charts

### Bar Chart
```javascript
slide.addChart(pres.charts.BAR, [{
  name: "Revenue",
  labels: ["2021", "2022", "2023", "2024"],
  values: [100, 150, 200, 280]
}], {
  x: 0.5, y: 1.5, w: 9, h: 3.5,
  barDir: "col",        // col, bar
  showTitle: true,
  title: "Revenue Trend (Billion CNY)",
  titleFontSize: 14,
  chartColors: ["1A365D"],
  showValue: true,
  dataLabelPosition: "outEnd",
  dataLabelColor: "2D3748"
});
```

### Line Chart
```javascript
slide.addChart(pres.charts.LINE, [{
  name: "Stock Price",
  labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
  values: [100, 105, 98, 112, 118, 125]
}], {
  x: 0.5, y: 1.5, w: 9, h: 3.5,
  lineSize: 2,
  lineSmooth: true,
  showTitle: true,
  title: "Stock Price Trend",
  chartColors: ["1A365D"],
  showMarker: true,
  showLegend: false
});
```

### Pie/Doughnut Chart
```javascript
slide.addChart(pres.charts.DOUGHNUT, [{
  name: "Market Share",
  labels: ["Company A", "Company B", "Company C", "Others"],
  values: [35, 25, 20, 20]
}], {
  x: 0.5, y: 1.5, w: 5, h: 3.5,
  showTitle: true,
  title: "Market Share",
  chartColors: ["1A365D", "38A169", "C9A227", "E2E8F0"],
  showPercent: true,
  showLegend: true,
  legendPos: "r"
});
```

## Tables

```javascript
slide.addTable([
  [
    { text: "指标", options: { fill: { color: "1A365D" }, color: "FFFFFF", bold: true } },
    { text: "2023", options: { fill: { color: "1A365D" }, color: "FFFFFF", bold: true } },
    { text: "2024", options: { fill: { color: "1A365D" }, color: "FFFFFF", bold: true } }
  ],
  ["营收", "200亿", "280亿"],
  ["净利润", "25亿", "35亿"],
  ["ROE", "15%", "18%"]
], {
  x: 0.5, y: 1.5, w: 9, h: 3,
  colW: [3, 3, 3],
  border: { pt: 0.5, color: "E2E8F0" },
  fontFace: "Arial",
  fontSize: 12,
  color: "2D3748",
  align: "center",
  valign: "middle"
});
```

## Common Patterns

### Page Number Badge
```javascript
function addPageBadge(slide, pres, pageNum) {
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.accent }
  });
  slide.addText(String(pageNum), {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
}
```

### Key Metric Card
```javascript
function addMetricCard(slide, x, y, label, value, change) {
  // Background
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: x, y: y, w: 2.8, h: 1.5,
    fill: { color: theme.light },
    rectRadius: 0.1
  });

  // Label
  slide.addText(label, {
    x: x, y: y + 0.15, w: 2.8, h: 0.4,
    fontSize: 12, fontFace: "Microsoft YaHei",
    color: theme.secondary, align: "center"
  });

  // Value
  slide.addText(value, {
    x: x, y: y + 0.5, w: 2.8, h: 0.6,
    fontSize: 24, fontFace: "Arial",
    color: theme.primary, bold: true, align: "center"
  });

  // Change indicator
  slide.addText(change, {
    x: x, y: y + 1.1, w: 2.8, h: 0.3,
    fontSize: 11, fontFace: "Arial",
    color: change.startsWith("+") ? "38A169" : "E53E3E",
    align: "center"
  });
}
```

## Export

```javascript
// Write to file
pres.writeFile({ fileName: "./output/presentation.pptx" })
  .then(() => console.log("Created: presentation.pptx"))
  .catch(err => console.error(err));
```

## Constants

| Constant | Value |
|----------|-------|
| LAYOUT_16x9 | 10" x 5.625" |
| LAYOUT_WIDE | 13.333" x 5.625" |
| LAYOUT_4x3 | 10" x 7.5" |

## Shape Types
- RECTANGLE
- ROUNDED_RECTANGLE
- OVAL
- LINE
- ARC
- PIE
- TEXT_BOX

## Chart Types
- BAR
- LINE
- PIE
- DOUGHNUT
- SCATTER
- BUBBLE
- RADAR
