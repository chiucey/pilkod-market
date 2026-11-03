# Slide Types Reference

## 5 Core Slide Types

### 1. Cover Page (封面)
- **Purpose**: Title and branding
- **Design**: Full background color, centered title
- **No page number badge**

```javascript
function createCoverSlide(pres, theme, title, subtitle) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  slide.addText(title, {
    x: 0.5, y: 2.0, w: 9, h: 1.2,
    fontSize: 44, fontFace: "Arial",
    color: "FFFFFF", bold: true, align: "center"
  });

  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.5, y: 3.3, w: 9, h: 0.6,
      fontSize: 20, fontFace: "Microsoft YaHei",
      color: theme.light, align: "center"
    });
  }

  return slide;
}
```

### 2. Table of Contents (目录)
- **Purpose**: Navigation guide
- **Design**: Clean layout with numbered items

```javascript
function createTOCSlide(pres, theme, items) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText("目录", {
    x: 0.5, y: 0.5, w: 9, h: 0.8,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  items.forEach((item, i) => {
    slide.addText(`${i + 1}. ${item}`, {
      x: 1.0, y: 1.5 + i * 0.6, w: 8, h: 0.5,
      fontSize: 18, fontFace: "Microsoft YaHei",
      color: theme.secondary
    });
  });

  // Page badge
  addPageBadge(slide, pres, 2);

  return slide;
}
```

### 3. Section Divider (章节分隔)
- **Purpose**: Mark new sections
- **Design**: Large section number + title

```javascript
function createSectionSlide(pres, theme, sectionNum, title) {
  const slide = pres.addSlide();
  slide.background = { color: theme.accent };

  slide.addText(`0${sectionNum}`, {
    x: 0.5, y: 1.5, w: 9, h: 1.5,
    fontSize: 72, fontFace: "Arial",
    color: theme.primary, bold: true, align: "center"
  });

  slide.addText(title, {
    x: 0.5, y: 3.2, w: 9, h: 0.8,
    fontSize: 36, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true, align: "center"
  });

  return slide;
}
```

### 4. Content Slide (内容页)
- **Purpose**: Main content delivery
- **Design**: Flexible layouts with text, charts, tables

#### Text + Bullet Layout
```javascript
function createContentSlide(pres, theme, title, bullets) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // Title
  slide.addText(title, {
    x: 0.5, y: 0.4, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // Bullets
  bullets.forEach((text, i) => {
    slide.addText(text, {
      x: 0.8, y: 1.3 + i * 0.5, w: 8.4, h: 0.45,
      fontSize: 16, fontFace: "Microsoft YaHei",
      color: theme.secondary, bullet: true
    });
  });

  // Page badge
  addPageBadge(slide, pres, pageNum);

  return slide;
}
```

#### Chart Layout
```javascript
function createChartSlide(pres, theme, title, chartImagePath, caption) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText(title, {
    x: 0.5, y: 0.4, w: 9, h: 0.7,
    fontSize: 28, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  slide.addImage(chartImagePath, {
    x: 0.5, y: 1.2, w: 9, h: 3.8,
    fit: "contain"
  });

  if (caption) {
    slide.addText(caption, {
      x: 0.5, y: 5.0, w: 9, h: 0.4,
      fontSize: 12, fontFace: "Arial",
      color: theme.secondary, align: "center", italic: true
    });
  }

  addPageBadge(slide, pres, pageNum);
  return slide;
}
```

### 5. Summary Slide (总结页)
- **Purpose**: Key takeaways
- **Design**: Numbered key points, call to action

```javascript
function createSummarySlide(pres, theme, keyPoints) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  slide.addText("核心要点", {
    x: 0.5, y: 0.5, w: 9, h: 0.8,
    fontSize: 32, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true, align: "center"
  });

  keyPoints.forEach((point, i) => {
    slide.addText(`${i + 1}. ${point}`, {
      x: 1.0, y: 1.6 + i * 0.8, w: 8, h: 0.7,
      fontSize: 20, fontFace: "Microsoft YaHei",
      color: "FFFFFF"
    });
  });

  return slide;
}
```

---

## Additional Layout Patterns

### Two-Column Layout
```javascript
function createTwoColumnSlide(pres, theme, title, leftContent, rightContent) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText(title, {
    x: 0.5, y: 0.3, w: 9, h: 0.6,
    fontSize: 26, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // Left column
  slide.addText(leftContent, {
    x: 0.5, y: 1.1, w: 4.3, h: 4.2,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: theme.secondary, valign: "top"
  });

  // Right column
  slide.addText(rightContent, {
    x: 5.2, y: 1.1, w: 4.3, h: 4.2,
    fontSize: 14, fontFace: "Microsoft YaHei",
    color: theme.secondary, valign: "top"
  });

  addPageBadge(slide, pres, pageNum);
  return slide;
}
```

### Table Layout
```javascript
function createTableSlide(pres, theme, title, headers, rows) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  slide.addText(title, {
    x: 0.5, y: 0.3, w: 9, h: 0.6,
    fontSize: 26, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  slide.addTable([headers, ...rows], {
    x: 0.5, y: 1.0, w: 9, h: 4.2,
    colW: [2, 2, 2, 3],
    border: { pt: 0.5, color: theme.light },
    fontFace: "Arial",
    fontSize: 12,
    color: theme.secondary,
    align: "center",
    valign: "middle"
  });

  addPageBadge(slide, pres, pageNum);
  return slide;
}
```
