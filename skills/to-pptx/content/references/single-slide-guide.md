# 单页PPT生成指南

本指南说明如何生成单页PPT，适用于快速创建独立的幻灯片。

---

## 使用场景

- 用户要求"生成一页PPT"
- 内容简单，只需一页展示
- 快速原型/演示

---

## 命名规范

单页PPT文件命名格式：`slide-[主题]-[类型].js`

示例：
- `slide-cover-intro.js` - 介绍封面
- `slide-content-flow.js` - 流程内容页
- `slide-summary-end.js` - 结束总结页

---

## 文件结构

```javascript
// slide-example.js
const pptxgen = require("pptxgenjs");

const slideConfig = {
  type: 'content',
  index: 1,
  title: '页面标题'
};

function createSlide(pres, theme) {
  const slide = pres.addSlide();
  slide.background = { color: theme.bg };
  return slide;
}

if (require.main === module) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_16x9';
  const theme = {
    primary: "22223b",
    secondary: "4a4e69",
    accent: "9a8c98",
    light: "c9ada7",
    bg: "f2e9e4"
  };
  createSlide(pres, theme);
  pres.writeFile({ fileName: "output.pptx" });
}

module.exports = { createSlide, slideConfig };
```

---

## 生成命令

```bash
cd /workspace/slides
node slide-example.js
```

---

## Theme对象说明

| 键 | 用途 | 示例 |
|-----|------|------|
| `primary` | 标题/深色文字 | "22223b" |
| `secondary` | 正文/次要文字 | "4a4e69" |
| `accent` | 强调/装饰色 | "9a8c98" |
| `light` | 浅色装饰 | "c9ada7" |
| `bg` | 背景色 | "f2e9e4" |
