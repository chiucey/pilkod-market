# 咨询顾问PPT幻灯片模板

本文档提供各类幻灯片的完整代码模板。

## 通用设置

```javascript
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";

// 咨询顾问主题色
const theme = {
  primary: "003366",    // 深海蓝
  secondary: "004B8D",  // 宝石蓝
  accent: "0066CC",      // 商务蓝
  light: "E6F0FF",       // 天空蓝
  bg: "FFFFFF",          // 白色背景
  text: "333333",        // 深灰文字
  gray: "666666"         // 中灰文字
};

// 页码辅助函数
function addPageNumber(pres, slide, num) {
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.primary }
  });
  slide.addText(String(num), {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
}
```

---

## 1. 封面页 (Cover)

### 1.1 标准封面

```javascript
// slide-01-cover.js
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: "cover",
  index: 1,
  title: "封面"
};

function createSlide(pres, theme, data) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 顶部装饰条
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.08,
    fill: { color: theme.primary }
  });

  // 左侧装饰条
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.08, h: 5.625,
    fill: { color: theme.secondary }
  });

  // 公司/项目名称
  slide.addText(data.company || "公司名称", {
    x: 0.5, y: 1.5, w: 9, h: 0.5,
    fontSize: 16, fontFace: "Microsoft YaHei",
    color: theme.secondary, align: "center"
  });

  // 主标题
  slide.addText(data.mainTitle || "主标题", {
    x: 0.5, y: 2.1, w: 9, h: 1.0,
    fontSize: 40, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true, align: "center"
  });

  // 副标题
  if (data.subTitle) {
    slide.addText(data.subTitle, {
      x: 0.5, y: 3.2, w: 9, h: 0.6,
      fontSize: 22, fontFace: "Microsoft YaHei",
      color: theme.text, align: "center"
    });
  }

  // 分隔装饰
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 4, y: 3.9, w: 2, h: 0.04,
    fill: { color: theme.accent }
  });

  // slogan
  if (data.slogan) {
    slide.addText(data.slogan, {
      x: 0.5, y: 4.1, w: 9, h: 0.4,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: theme.gray, align: "center"
    });
  }

  // 版权声明
  slide.addText("©版权声明 | 商业秘密未经许可不得外泄", {
    x: 0.5, y: 5.2, w: 9, h: 0.3,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: theme.gray, align: "center"
  });

  return slide;
}

// 独立预览
if (require.main === module) {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  const theme = {
    primary: "003366",
    secondary: "004B8D",
    accent: "0066CC",
    light: "E6F0FF",
    bg: "FFFFFF",
    text: "333333",
    gray: "666666"
  };
  createSlide(pres, theme, {
    company: "中能智新科技产业发展有限公司",
    mainTitle: "项目需求沟通材料",
    subTitle: "战略规划咨询项目",
    slogan: "学无罔 / 思无殆 / 言有物 / 行有恒"
  });
  pres.writeFile({ fileName: "cover-preview.pptx" });
}

module.exports = { createSlide, slideConfig };
```

### 1.2 深色背景封面

```javascript
// slide-01-dark-cover.js
function createSlide(pres, theme, data) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  // 装饰线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 2.2, w: 0.1, h: 1.5,
    fill: { color: "FFFFFF" }
  });

  // 章节编号
  slide.addText(data.sectionNum || "01", {
    x: 0.8, y: 1.8, w: 2, h: 1.2,
    fontSize: 72, fontFace: "Arial",
    color: "FFFFFF", bold: true
  });

  // 主标题
  slide.addText(data.mainTitle, {
    x: 0.8, y: 3.0, w: 8, h: 1.0,
    fontSize: 36, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true
  });

  // 副标题
  if (data.subTitle) {
    slide.addText(data.subTitle, {
      x: 0.8, y: 4.0, w: 8, h: 0.5,
      fontSize: 18, fontFace: "Microsoft YaHei",
      color: theme.light
    });
  }

  return slide;
}
```

---

## 2. 目录页 (TOC)

```javascript
// slide-02-toc.js
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: "toc",
  index: 2,
  title: "目录"
};

function createSlide(pres, theme, chapters) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 页面标题
  slide.addText("目录", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 28, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 标题下分隔线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.0, w: 1.2, h: 0.04,
    fill: { color: theme.primary }
  });

  // 章节布局 - 左右两列
  chapters.forEach((chapter, index) => {
    const col = index < 3 ? 0 : 1;
    const row = index % 3;
    const x = col === 0 ? 1.2 : 5.5;
    const y = 1.5 + row * 1.2;

    // 编号圆圈
    slide.addShape(pres.shapes.OVAL, {
      x: x, y: y, w: 0.6, h: 0.6,
      fill: { color: theme.primary }
    });
    slide.addText(chapter.num, {
      x: x, y: y, w: 0.6, h: 0.6,
      fontSize: 18, fontFace: "Arial",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });

    // 章节名称
    slide.addText(chapter.name, {
      x: x + 0.8, y: y, w: 3.5, h: 0.6,
      fontSize: 20, fontFace: "Microsoft YaHei",
      color: theme.text, valign: "middle"
    });

    // 描述（如果有）
    if (chapter.desc) {
      slide.addText(chapter.desc, {
        x: x + 0.8, y: y + 0.5, w: 3.5, h: 0.4,
        fontSize: 11, fontFace: "Microsoft YaHei",
        color: theme.gray
      });
    }
  });

  // 页码
  addPageNumber(pres, slide, 2);

  return slide;
}

function addPageNumber(pres, slide, num) {
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.primary }
  });
  slide.addText(String(num), {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
}

module.exports = { createSlide, slideConfig };
```

---

## 3. 章节分隔页 (Section Divider)

```javascript
// slide-section.js
function createSectionSlide(pres, theme, sectionNum, sectionTitle, subTitle) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  // 大号章节编号
  slide.addText(String(sectionNum).padStart(2, "0"), {
    x: 0.8, y: 1.5, w: 2.5, h: 2.5,
    fontSize: 120, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    transparency: 30
  });

  // 章节标题
  slide.addText(sectionTitle, {
    x: 0.8, y: 2.3, w: 8, h: 1.0,
    fontSize: 36, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true
  });

  // 装饰线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.8, y: 3.4, w: 2.5, h: 0.06,
    fill: { color: "FFFFFF" }
  });

  // 副标题（如果有）
  if (subTitle) {
    slide.addText(subTitle, {
      x: 0.8, y: 3.7, w: 8, h: 0.5,
      fontSize: 18, fontFace: "Microsoft YaHei",
      color: theme.light
    });
  }

  return slide;
}
```

---

## 4. 内容页模板

### 4.1 文本列表型

```javascript
// slide-content-list.js
function createTextListSlide(pres, theme, data) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 页面标题
  slide.addText(data.title, {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 24, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 分隔线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.0, w: 1.5, h: 0.04,
    fill: { color: theme.primary }
  });

  // 内容项
  data.items.forEach((item, index) => {
    const y = 1.3 + index * 0.85;

    // 编号
    slide.addText(`${index + 1}.`, {
      x: 0.5, y: y, w: 0.4, h: 0.5,
      fontSize: 16, fontFace: "Arial",
      color: theme.primary, bold: true
    });

    // 标题
    slide.addText(item.title, {
      x: 0.9, y: y, w: 8.5, h: 0.4,
      fontSize: 16, fontFace: "Microsoft YaHei",
      color: theme.text, bold: true
    });

    // 描述
    if (item.desc) {
      slide.addText(item.desc, {
        x: 0.9, y: y + 0.35, w: 8.5, h: 0.45,
        fontSize: 12, fontFace: "Microsoft YaHei",
        color: theme.gray
      });
    }
  });

  // 来源（如果有）
  if (data.source) {
    slide.addText(`数据来源：${data.source}`, {
      x: 0.5, y: 5.1, w: 9, h: 0.3,
      fontSize: 10, fontFace: "Microsoft YaHei",
      color: theme.gray
    });
  }

  // 页码
  addPageNumber(pres, slide, data.pageNum || 3);

  return slide;
}
```

### 4.2 表格型

```javascript
// slide-content-table.js
function createTableSlide(pres, theme, data) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 页面标题
  slide.addText(data.title, {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 24, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 分隔线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.0, w: 1.5, h: 0.04,
    fill: { color: theme.primary }
  });

  // 表格数据
  const tableRows = [
    // 表头
    data.headers.map(h => ({
      text: h,
      options: {
        fill: { color: theme.primary },
        color: "FFFFFF",
        bold: true,
        align: "center",
        valign: "middle"
      }
    })),
    // 数据行
    ...data.rows.map((row, rowIndex) =>
      row.map(cell => ({
        text: String(cell),
        options: {
          fill: { color: rowIndex % 2 === 0 ? theme.bg : theme.light },
          color: theme.text,
          align: "center",
          valign: "middle"
        }
      }))
    )
  ];

  slide.addTable(tableRows, {
    x: 0.5, y: 1.2, w: 9, h: 3.4,
    fontFace: "Microsoft YaHei",
    fontSize: 11,
    border: { pt: 0.5, color: "CCCCCC" },
    colW: data.colWidths || [],
    rowH: 0.45
  });

  // 来源
  if (data.source) {
    slide.addText(`数据来源：${data.source}`, {
      x: 0.5, y: 4.8, w: 9, h: 0.3,
      fontSize: 10, fontFace: "Microsoft YaHei",
      color: theme.gray
    });
  }

  // 页码
  addPageNumber(pres, slide, data.pageNum || 4);

  return slide;
}
```

### 4.3 图表型

```javascript
// slide-content-chart.js
function createChartSlide(pres, theme, data) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 页面标题
  slide.addText(data.title, {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 24, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 分隔线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.0, w: 1.5, h: 0.04,
    fill: { color: theme.primary }
  });

  // 图表
  const chartType = {
    "bar": pres.charts.BAR,
    "line": pres.charts.LINE,
    "pie": pres.charts.PIE
  }[data.chartType] || pres.charts.BAR;

  slide.addChart(chartType, data.chartData, {
    x: 0.5, y: 1.2, w: 5.8, h: 3.5,
    showTitle: false,
    showLegend: true,
    legendPos: "b",
    chartColors: [theme.primary, theme.secondary, theme.accent, theme.light],
    catAxisLabelColor: theme.gray,
    catAxisLabelFontSize: 10,
    valAxisLabelColor: theme.gray,
    valAxisLabelFontSize: 10,
    valGridLine: { color: "E5E5E5", size: 0.5 },
    catGridLine: { style: "none" },
    barDir: data.barDir || "bar"
  });

  // 右侧关键洞察
  if (data.insights && data.insights.length > 0) {
    data.insights.forEach((insight, index) => {
      // 关键数字
      if (insight.value) {
        slide.addText(insight.value, {
          x: 6.6, y: 1.3 + index * 1.2, w: 3, h: 0.6,
          fontSize: 32, fontFace: "Arial",
          color: theme.primary, bold: true
        });
      }
      // 说明文字
      if (insight.label) {
        slide.addText(insight.label, {
          x: 6.6, y: 1.85 + index * 1.2, w: 3, h: 0.4,
          fontSize: 12, fontFace: "Microsoft YaHei",
          color: theme.text
        });
      }
    });
  }

  // 来源
  if (data.source) {
    slide.addText(`数据来源：${data.source}`, {
      x: 0.5, y: 4.9, w: 9, h: 0.3,
      fontSize: 10, fontFace: "Microsoft YaHei",
      color: theme.gray
    });
  }

  // 页码
  addPageNumber(pres, slide, data.pageNum || 5);

  return slide;
}
```

### 4.4 多列卡片型

```javascript
// slide-content-cards.js
function createCardsSlide(pres, theme, data) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 页面标题
  slide.addText(data.title, {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 24, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 分隔线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.0, w: 1.5, h: 0.04,
    fill: { color: theme.primary }
  });

  // 卡片布局
  const cardWidth = 4.3;
  const cardHeight = 1.6;
  const gapX = 0.4;
  const gapY = 0.3;
  const startX = 0.5;
  const startY = 1.3;

  data.cards.forEach((card, index) => {
    const col = index % 2;
    const row = Math.floor(index / 2);
    const x = startX + col * (cardWidth + gapX);
    const y = startY + row * (cardHeight + gapY);

    // 卡片背景
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: y, w: cardWidth, h: cardHeight,
      fill: { color: theme.light },
      rectRadius: 0.1
    });

    // 编号圆圈
    slide.addShape(pres.shapes.OVAL, {
      x: x + 0.2, y: y + 0.2, w: 0.45, h: 0.45,
      fill: { color: theme.primary }
    });
    slide.addText(String(index + 1), {
      x: x + 0.2, y: y + 0.2, w: 0.45, h: 0.45,
      fontSize: 14, fontFace: "Arial",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });

    // 卡片标题
    slide.addText(card.title, {
      x: x + 0.8, y: y + 0.2, w: cardWidth - 1.0, h: 0.45,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: theme.primary, bold: true,
      valign: "middle"
    });

    // 卡片内容
    slide.addText(card.content, {
      x: x + 0.2, y: y + 0.75, w: cardWidth - 0.4, h: cardHeight - 0.95,
      fontSize: 11, fontFace: "Microsoft YaHei",
      color: theme.text
    });
  });

  // 页码
  addPageNumber(pres, slide, data.pageNum || 6);

  return slide;
}
```

---

## 5. 总结页 (Summary)

```javascript
// slide-summary.js
function createSummarySlide(pres, theme, data) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 页面标题
  slide.addText(data.title || "总结", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 28, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 分隔线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.0, w: 1.2, h: 0.04,
    fill: { color: theme.primary }
  });

  // 总结要点
  data.points.forEach((point, index) => {
    const y = 1.3 + index * 0.9;

    // 编号
    slide.addShape(pres.shapes.OVAL, {
      x: 0.5, y: y, w: 0.5, h: 0.5,
      fill: { color: theme.primary }
    });
    slide.addText(String(index + 1), {
      x: 0.5, y: y, w: 0.5, h: 0.5,
      fontSize: 16, fontFace: "Arial",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });

    // 内容
    slide.addText(point, {
      x: 1.2, y: y, w: 8.2, h: 0.5,
      fontSize: 14, fontFace: "Microsoft YaHei",
      color: theme.text, valign: "middle"
    });
  });

  // Q&A
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 3.5, y: 4.5, w: 3, h: 0.7,
    fill: { color: theme.primary },
    rectRadius: 0.1
  });
  slide.addText("Q & A", {
    x: 3.5, y: 4.5, w: 3, h: 0.7,
    fontSize: 24, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });

  // 页码
  addPageNumber(pres, slide, data.pageNum || 99);

  return slide;
}
```

---

## 编译脚本模板

```javascript
// compile.js
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";

// 咨询顾问主题色
const theme = {
  primary: "003366",
  secondary: "004B8D",
  accent: "0066CC",
  light: "E6F0FF",
  bg: "FFFFFF",
  text: "333333",
  gray: "666666"
};

// 加载并执行各幻灯片模块
const slideCount = 12; // 根据实际幻灯片数量调整

for (let i = 1; i <= slideCount; i++) {
  const num = String(i).padStart(2, "0");
  try {
    const slideModule = require(`./slide-${num}.js`);
    slideModule.createSlide(pres, theme);
    console.log(`✓ Slide ${num} loaded`);
  } catch (err) {
    console.error(`✗ Error loading slide-${num}.js:`, err.message);
  }
}

// 输出文件
pres.writeFile({ fileName: "./output/presentation.pptx" })
  .then(() => {
    console.log("\n✓ PPT generated: ./output/presentation.pptx");
  })
  .catch(err => {
    console.error("Error writing file:", err);
  });
```

---

## 使用示例

```javascript
// 示例：创建项目沟通材料PPT

const slides = [
  { type: "cover", data: {
    company: "中能智新科技产业发展有限公司",
    mainTitle: "项目需求沟通材料",
    slogan: "学无罔 / 思无殆 / 言有物 / 行有恒"
  }},
  { type: "toc", data: {
    chapters: [
      { num: "一", name: "正略公司介绍" },
      { num: "二", name: "项目需求理解" },
      { num: "三", name: "外部案例分享" },
      { num: "四", name: "项目计划安排" }
    ]
  }},
  // ... 更多幻灯片
];

// 根据类型生成对应幻灯片
slides.forEach((slide, index) => {
  switch(slide.type) {
    case "cover":
      createCoverSlide(pres, theme, slide.data);
      break;
    case "toc":
      createTOCSlide(pres, theme, slide.data.chapters);
      break;
    // ...
  }
});
```
