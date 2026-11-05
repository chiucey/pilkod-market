# Design System Reference

## Color Palette Reference

### Financial/Business Reports
```javascript
const financialPalette = {
  primary: "1A365D",    // Deep blue - professional, trustworthy
  secondary: "2D3748",  // Dark gray - readable body text
  accent: "C9A227",     // Gold - highlights, key metrics
  light: "E2E8F0",      // Light gray - backgrounds, dividers
  bg: "FFFFFF"          // White - clean base
};
```

### Technology/Growth Companies
```javascript
const techPalette = {
  primary: "1E3A5F",    // Navy blue
  secondary: "4A5568",  // Medium gray
  accent: "38B2AC",     // Teal - modern, tech-forward
  light: "E6FFFA",      // Light teal
  bg: "FFFFFF"
};
```

### Energy/Sustainability
```javascript
const greenPalette = {
  primary: "22543D",    // Forest green
  secondary: "276749",  // Green
  accent: "D69E2E",     // Gold
  light: "F0FFF4",      // Light green tint
  bg: "FFFFFF"
};
```

### Conservative/Traditional
```javascript
const conservativePalette = {
  primary: "1A202C",    // Near black
  secondary: "2D3748",  // Dark gray
  accent: "718096",     // Medium gray
  light: "EDF2F7",      // Light gray
  bg: "FFFFFF"
};
```

---

## Font Reference

### Font Families
| Language | Primary | Secondary |
|----------|---------|----------|
| Chinese | Microsoft YaHei | SimHei |
| English | Arial | Calibri |
| Numbers | Roboto Mono | Courier |

### Font Sizes
| Element | Size | Weight |
|---------|------|--------|
| H1 (Cover title) | 44pt | Bold |
| H2 (Slide title) | 28-32pt | Bold |
| H3 (Section) | 20-24pt | SemiBold |
| Body | 14-16pt | Regular |
| Caption | 10-12pt | Regular |
| Table | 11-14pt | Regular |

---

## Style Recipes

### Sharp Style
- Clean, angular corners
- High contrast
- Minimal shadows
- Professional appearance

```javascript
const sharpTheme = {
  primary: "1A1A1A",
  secondary: "4A4A4A",
  accent: "C00000",
  light: "E0E0E0",
  bg: "FFFFFF"
};
```

### Soft Style
- Subtle rounded corners (0.1-0.2")
- Medium contrast
- Light shadows
- Approachable feel

```javascript
const softTheme = {
  primary: "2D3748",
  secondary: "718096",
  accent: "38A169",
  light: "EDF2F7",
  bg: "FFFFFF"
};
```

### Rounded Style
- Large rounded corners (0.3-0.5")
- Low contrast
- Soft shadows
- Friendly, modern

```javascript
const roundedTheme = {
  primary: "4A5568",
  secondary: "A0AEC0",
  accent: "4299E1",
  light: "EBF8FF",
  bg: "FFFFFF"
};
```

### Pill Style
- Fully rounded elements
- Gradient backgrounds
- Bold colors
- Eye-catching

```javascript
const pillTheme = {
  primary: "553C9A",
  secondary: "6B46C1",
  accent: "ED64A6",
  light: "FAF5FF",
  bg: "FFFFFF"
};
```

---

## Typography Guidelines

### Line Spacing
- Headlines: 1.2x line height
- Body text: 1.4x line height
- Tight text: 1.2x line height

### Margins & Padding
- Slide margins: 0.5" all sides
- Content padding: 0.3"
- Between elements: 0.2-0.3"

### Text Alignment
- Headlines: Center or Left
- Body: Left
- Numbers in tables: Center or Right
- Captions: Center

---

## Chart Color Strategy

### Company Brand Colors
When the report focuses on a specific company, use their brand colors:
- Tesla: `#E82127`
- Apple: `#555555`
- BYD: `#1E4D8C`
- Microsoft: `#00A4EF`

### Multi-Company Comparison
Assign each company its brand color:
```javascript
const companyColors = {
  "Tesla": "#E82127",
  "BYD": "#1E4D8C",
  "NIO": "#3C6EE5",
  "Xpeng": "#D92B2B"
};
```

### Professional Business Palette
For industry reports without a single brand:
```javascript
const businessColors = ["#1A1A1A", "#4A4A4A", "#B8860B", "#6B6B6B", "#9B9B9B"];
```
