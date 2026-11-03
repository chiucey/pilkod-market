---
name: consulting-ppt-generator
description: 生成专业咨询顾问风格的PPT演示文稿。当用户要求创建咨询公司风格PPT（如麦肯锡、贝恩、正略等咨询公司风格）、商业咨询报告PPT、企业战略规划PPT、市场分析PPT、国企/央企汇报材料PPT，或参考正略咨询PPT风格生成PPT时使用此技能。
---

# 咨询顾问PPT生成器

生成专业咨询顾问风格的PPT演示文稿，参考正略咨询、麦肯锡等顶级咨询公司的视觉标准。

## 咨询顾问风格设计系统

### 配色方案

咨询顾问PPT采用专业、权威的蓝色系配色：

| 用途 | 颜色名称 | Hex值 |
|------|----------|-------|
| 主色 | 深海蓝 | `003366` |
| 次要色 | 宝石蓝 | `004B8D` |
| 强调色 | 商务蓝 | `0066CC` |
| 浅色 | 天空蓝 | `E6F0FF` |
| 背景色 | 纯白 | `FFFFFF` |
| 文字色 | 深灰 | `333333` |
| 辅助文字 | 中灰 | `666666` |

### 字体规范

- **中文**：微软雅黑 (Microsoft YaHei)
- **英文**：Arial
- **标题**：加粗，24-36pt
- **副标题**：加粗，18-24pt
- **正文**：常规，14-16pt
- **注释/来源**：10-12pt

### 布局规范

- 页面尺寸：10" x 5.625" (16:9)
- 页边距：0.5"
- 标题区域：顶部 0.3"-0.8"
- 内容区域：中部 1.2"-4.8"
- 页码区域：右下角 x:9.3", y:5.1"

---

## 工作流程

### 步骤1：需求收集

使用GenUI表单收集PPT需求：

1. **基本信息**：标题、副标题、公司/项目名称
2. **内容结构**：章节数量、每章节主题
3. **详细内容**：各章节具体要点
4. **风格确认**：使用咨询蓝配色方案

### 步骤2：生成幻灯片

根据咨询顾问风格自动生成每页幻灯片：

| 幻灯片类型 | 用途 | 特征 |
|-----------|------|------|
| 封面页 | 开场 | 标题居中、副标题、logo位置、版权声明 |
| 目录页 | 导航 | 章节编号、章节名称 |
| 章节页 | 分隔 | 章节编号、大标题、简洁背景 |
| 内容页 | 核心 | 标题 + 多列/表格/图表布局 |
| 总结页 | 收尾 | 核心要点回顾、Q&A |

### 步骤3：编译输出

使用PptxGenJS编译生成PPTX文件：
- 每页独立JS模块
- 统一主题配置
- 批量编译

---

## 幻灯片类型模板

### 1. 封面页 (Cover)

```javascript
function createCoverSlide(pres, theme, data) {
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

  // 主标题
  slide.addText(data.mainTitle, {
    x: 0.5, y: 1.8, w: 9, h: 1.2,
    fontSize: 40, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true, align: "center"
  });

  // 副标题
  if (data.subTitle) {
    slide.addText(data.subTitle, {
      x: 0.5, y: 3.0, w: 9, h: 0.6,
      fontSize: 20, fontFace: "Microsoft YaHei",
      color: theme.secondary, align: "center"
    });
  }

  // 公司/项目名称
  if (data.company) {
    slide.addText(data.company, {
      x: 0.5, y: 3.8, w: 9, h: 0.5,
      fontSize: 18, fontFace: "Microsoft YaHei",
      color: theme.text, align: "center"
    });
  }

  // 底部版权声明
  slide.addText("©版权声明 | 商业秘密未经许可不得外泄", {
    x: 0.5, y: 5.2, w: 9, h: 0.3,
    fontSize: 10, fontFace: "Microsoft YaHei",
    color: theme.gray, align: "center"
  });

  return slide;
}
```

### 2. 目录页 (TOC)

```javascript
function createTOCSlide(pres, theme, chapters) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 页面标题
  slide.addText("目录", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 28, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 章节列表 - 左右两列布局
  chapters.forEach((chapter, index) => {
    const col = index < 3 ? 0 : 1;
    const row = index % 3;
    const x = col === 0 ? 1.2 : 5.5;
    const y = 1.4 + row * 1.2;

    // 章节编号圆圈
    slide.addShape(pres.shapes.OVAL, {
      x: x, y: y, w: 0.5, h: 0.5,
      fill: { color: theme.primary }
    });
    slide.addText(chapter.num, {
      x: x, y: y, w: 0.5, h: 0.5,
      fontSize: 16, fontFace: "Arial",
      color: "FFFFFF", bold: true,
      align: "center", valign: "middle"
    });

    // 章节名称
    slide.addText(chapter.name, {
      x: x + 0.7, y: y, w: 3, h: 0.5,
      fontSize: 18, fontFace: "Microsoft YaHei",
      color: theme.text, valign: "middle"
    });
  });

  // 页码
  slide.addText("2", { /* 页码位置 */ });

  return slide;
}
```

### 3. 章节分隔页 (Section Divider)

```javascript
function createSectionSlide(pres, theme, sectionNum, sectionTitle) {
  const slide = pres.addSlide();
  slide.background = { color: theme.primary };

  // 大号章节编号
  slide.addText(sectionNum, {
    x: 0.8, y: 1.5, w: 2, h: 2,
    fontSize: 100, fontFace: "Arial",
    color: "FFFFFF", bold: true
  });

  // 章节标题
  slide.addText(sectionTitle, {
    x: 2.8, y: 2.0, w: 6.5, h: 1.2,
    fontSize: 36, fontFace: "Microsoft YaHei",
    color: "FFFFFF", bold: true
  });

  // 装饰线
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 2.8, y: 3.3, w: 2, h: 0.06,
    fill: { color: "FFFFFF" }
  });

  return slide;
}
```

### 4. 内容页 (Content)

#### 4.1 文本列表型

```javascript
function createTextListSlide(pres, theme, title, items) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 页面标题
  slide.addText(title, {
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
  items.forEach((item, index) => {
    const y = 1.3 + index * 0.8;

    // 编号
    slide.addText(`${index + 1}.`, {
      x: 0.5, y: y, w: 0.4, h: 0.6,
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
        x: 0.9, y: y + 0.35, w: 8.5, h: 0.4,
        fontSize: 12, fontFace: "Microsoft YaHei",
        color: theme.gray
      });
    }
  });

  // 页码
  slide.addPageNumber(pres, theme);

  return slide;
}
```

#### 4.2 表格型

```javascript
function createTableSlide(pres, theme, title, tableData, options = {}) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 标题
  slide.addText(title, {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 24, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 表格
  const tableRows = [tableData.headers, ...tableData.rows];
  slide.addTable(tableRows, {
    x: 0.5, y: 1.2, w: 9, h: 3.5,
    fontFace: "Microsoft YaHei",
    fontSize: 11,
    color: theme.text,
    border: { pt: 0.5, color: "CCCCCC" },
    colW: tableData.colWidths || [],
    rowH: 0.4,
    fill: { color: theme.bg },
    valign: "middle",
    align: "center"
  });

  // 来源
  if (tableData.source) {
    slide.addText(`数据来源：${tableData.source}`, {
      x: 0.5, y: 5.0, w: 9, h: 0.3,
      fontSize: 10, fontFace: "Microsoft YaHei",
      color: theme.gray
    });
  }

  // 页码
  slide.addPageNumber(pres, theme);

  return slide;
}
```

#### 4.3 图表型

```javascript
function createChartSlide(pres, theme, title, chartType, chartData, options = {}) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 标题
  slide.addText(title, {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 24, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 图表
  slide.addChart(pres.charts[chartType], chartData.data, {
    x: 0.5, y: 1.0, w: 5.5, h: 3.5,
    showTitle: false,
    showLegend: true,
    legendPos: "b",
    chartColors: [theme.primary, theme.secondary, theme.accent, theme.light],
    catAxisLabelColor: theme.gray,
    valAxisLabelColor: theme.gray,
    valGridLine: { color: "E5E5E5", size: 0.5 }
  });

  // 右侧说明
  if (options.insights) {
    options.insights.forEach((insight, index) => {
      slide.addText(insight, {
        x: 6.3, y: 1.2 + index * 0.8, w: 3.2, h: 0.7,
        fontSize: 12, fontFace: "Microsoft YaHei",
        color: theme.text
      });
    });
  }

  // 来源
  if (options.source) {
    slide.addText(`数据来源：${options.source}`, {
      x: 0.5, y: 5.0, w: 9, h: 0.3,
      fontSize: 10, fontFace: "Microsoft YaHei",
      color: theme.gray
    });
  }

  // 页码
  slide.addPageNumber(pres, theme);

  return slide;
}
```

### 5. 总结页 (Summary)

```javascript
function createSummarySlide(pres, theme, title, keyPoints) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };

  // 标题
  slide.addText(title || "总结", {
    x: 0.5, y: 0.4, w: 9, h: 0.6,
    fontSize: 28, fontFace: "Microsoft YaHei",
    color: theme.primary, bold: true
  });

  // 要点卡片
  keyPoints.forEach((point, index) => {
    const x = index % 2 === 0 ? 0.5 : 5.0;
    const y = 1.3 + Math.floor(index / 2) * 1.5;

    // 卡片背景
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: y, w: 4.5, h: 1.2,
      fill: { color: theme.light },
      rectRadius: 0.1
    });

    // 编号
    slide.addText(`${index + 1}`, {
      x: x + 0.2, y: y + 0.2, w: 0.4, h: 0.4,
      fontSize: 20, fontFace: "Arial",
      color: theme.primary, bold: true
    });

    // 内容
    slide.addText(point, {
      x: x + 0.7, y: y + 0.2, w: 3.5, h: 0.9,
      fontSize: 13, fontFace: "Microsoft YaHei",
      color: theme.text
    });
  });

  // Q&A
  slide.addText("Q & A", {
    x: 0.5, y: 4.8, w: 9, h: 0.5,
    fontSize: 18, fontFace: "Arial",
    color: theme.secondary, align: "center"
  });

  // 页码
  slide.addPageNumber(pres, theme);

  return slide;
}
```

---

## 页码组件

```javascript
// 页码（封面页除外均需添加）
function addPageNumber(pres, theme, pageNum) {
  // 圆形页码
  slide.addShape(pres.shapes.OVAL, {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fill: { color: theme.primary }
  });
  slide.addText(String(pageNum), {
    x: 9.3, y: 5.1, w: 0.4, h: 0.4,
    fontSize: 12, fontFace: "Arial",
    color: "FFFFFF", bold: true,
    align: "center", valign: "middle"
  });
}
```

---

## 主题配置

```javascript
const consultingTheme = {
  primary: "003366",    // 深海蓝 - 主色调
  secondary: "004B8D",  // 宝石蓝 - 次要色
  accent: "0066CC",      // 商务蓝 - 强调色
  light: "E6F0FF",       // 天空蓝 - 浅色背景
  bg: "FFFFFF",          // 白色 - 页面背景
  text: "333333",        // 深灰 - 主要文字
  gray: "666666"         // 中灰 - 辅助文字
};
```

---

## 输出结构

```
slides/
├── slide-01.js          # 封面页
├── slide-02.js          # 目录页
├── slide-03.js          # 章节分隔页
├── slide-04.js          # 内容页
├── ...
├── slide-N.js           # 总结页
├── compile.js           # 编译脚本
└── output/              # 输出目录
    └── presentation.pptx
```

---

## 完整流程

1. **收集需求** → 使用GenUI表单
2. **生成幻灯片** → 按类型模板生成JS文件
3. **编译PPTX** → node compile.js
4. **输出文件** → slides/output/presentation.pptx

详细模板参考：[references/slide-templates.md](references/slide-templates.md)
设计系统参考：[references/design-system.md](references/design-system.md)
